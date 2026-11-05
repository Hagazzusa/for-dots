shader_type spatial;
render_mode unshaded, blend_mix, depth_draw_never, cull_disabled;
uniform float lamp_strength : hint_range(0.0, 1.0) = 0.0;
uniform float silhouette_progress : hint_range(0.0, 1.0) = 0.0;
uniform float silhouette_strength : hint_range(0.0, 1.0) = 0.0;
void fragment() {
 vec2 uv = UV;
 float center_x = mix(-0.17, 1.17, silhouette_progress);
 float head = 1.0-smoothstep(0.055,0.075,length(uv-vec2(center_x,0.43)));
 float torso = 1.0-smoothstep(0.85,1.05,length((uv-vec2(center_x,0.76))/vec2(0.115,0.27)));
 float silhouette = max(head,torso)*silhouette_strength;
 float edge = smoothstep(0.0,0.055,uv.x)*smoothstep(0.0,0.055,1.0-uv.x)*smoothstep(0.0,0.035,uv.y)*smoothstep(0.0,0.035,1.0-uv.y);
 float curtain = mix(0.72,1.0,smoothstep(0.06,0.15,uv.x)*smoothstep(0.06,0.15,1.0-uv.x));
 vec3 warm = vec3(0.48,0.30,0.15)*curtain*(1.0-0.78*silhouette);
 ALBEDO = warm;
 EMISSION = warm*0.35*lamp_strength;
 ALPHA = edge*lamp_strength*0.62;
}
