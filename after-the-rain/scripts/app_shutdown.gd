extends Node
## Owns app exit, not audio mixing. Session injects one terminal preparation command.
signal completed(timed_out: bool, remaining_playbacks: int)
@export_range(0.05,5.0) var release_timeout_seconds := 2.0
var requested := false
var finished := false
var _prepare: Callable
var _quit: Callable
var _pending: Array[WeakRef] = []
var _deadline_us := 0
var _owns_window_hook := false
var _previous_auto_quit := true
var _window: Window

func _ready() -> void:
 process_mode=Node.PROCESS_MODE_ALWAYS
 set_process(false)

func initialize(session: Node, prepare: Callable, quit_command: Callable = Callable()) -> void:
 _prepare=prepare
 _quit=quit_command if quit_command.is_valid() else get_tree().quit
 _install_window_hook.call_deferred(session)

func _install_window_hook(session: Node) -> void:
 # Embedded scene/test instances must not take over the application's close policy.
 if not is_instance_valid(session) or get_tree().current_scene!=session or _owns_window_hook:return
 _window=get_tree().root
 _previous_auto_quit=get_tree().auto_accept_quit
 get_tree().auto_accept_quit=false
 _window.close_requested.connect(request_shutdown)
 _owns_window_hook=true

func request_shutdown() -> bool:
 if requested:return false
 requested=true
 var seconds:=release_timeout_seconds if is_finite(release_timeout_seconds) else 2.0
 _deadline_us=Time.get_ticks_usec()+int(clampf(seconds,.05,5.0)*1000000.0)
 if _prepare.is_valid():_pending.assign(_prepare.call())
 set_process(true)
 _poll()
 return true

func _process(_delta: float) -> void:
 _poll()

func _poll() -> void:
 if not requested or finished:return
 var alive:=0
 for reference in _pending:
  if reference.get_ref()!=null:alive+=1
 var timed_out:=Time.get_ticks_usec()>=_deadline_us
 if alive>0 and not timed_out:return
 finished=true
 set_process(false)
 _pending.clear()
 if alive>0:push_warning("Audio shutdown deadline reached with %d playback references; exiting without an unbounded wait."%alive)
 completed.emit(alive>0,alive)
 if _quit.is_valid():_quit.call()

func _exit_tree() -> void:
 if _owns_window_hook and is_instance_valid(_window):
  if _window.close_requested.is_connected(request_shutdown):_window.close_requested.disconnect(request_shutdown)
  get_tree().auto_accept_quit=_previous_auto_quit
