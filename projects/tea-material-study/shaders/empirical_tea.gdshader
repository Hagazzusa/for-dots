shader_type spatial;
render_mode blend_mix, depth_draw_always, cull_back, diffuse_burley, specular_schlick_ggx;
// Cup-specific visual hint, not refraction, absorption or fluid simulation.
// No screen, depth or image textures. Original closed mesh is unchanged.
uniform vec2 cup_center_xz = vec2(-0.17, 0.165);
uniform float surface_y = 0.059;
uniform vec4 thin_amber : source_color = vec4(0.70, 0.34, 0.055, 1.0);
uniform vec4 deep_amber : source_color = vec4(0.44, 0.19, 0.045, 1.0);
uniform float thin_opacity : hint_range(0.0,1.0) = 0.40;
uniform float deep_opacity : hint_range(0.0,1.0) = 0.78;
uniform float surface_roughness : hint_range(0.02,0.5) = 0.11;
varying vec3 model_position;
float inner_bowl_height(float radius) {
    if (radius <= 0.020) { return 0.012; }
    if (radius <= 0.028) { return mix(0.012,0.013,(radius-0.020)/0.008); }
    if (radius <= 0.032) { return mix(0.013,0.015,(radius-0.028)/0.004); }
    if (radius <= 0.036) { return mix(0.015,0.019,(radius-0.032)/0.004); }
    if (radius <= 0.040) { return mix(0.019,0.028,(radius-0.036)/0.004); }
    if (radius <= 0.043) { return mix(0.028,0.041,(radius-0.040)/0.003); }
    if (radius <= 0.045) { return mix(0.041,0.055,(radius-0.043)/0.002); }
    return mix(0.055,0.068,clamp((radius-0.045)/0.001,0.0,1.0));
}
void vertex() { model_position = VERTEX; }
void fragment() {
    float radius = length(model_position.xz-cup_center_xz);
    float hint_depth = clamp((surface_y-inner_bowl_height(radius))/0.047,0.0,1.0);
    float blend_hint = smoothstep(0.0,1.0,hint_depth);
    ALBEDO = mix(thin_amber.rgb,deep_amber.rgb,blend_hint);
    ALPHA = mix(thin_opacity,deep_opacity,blend_hint);
    METALLIC = 0.0;
    ROUGHNESS = surface_roughness;
    SPECULAR = 0.5;
}
