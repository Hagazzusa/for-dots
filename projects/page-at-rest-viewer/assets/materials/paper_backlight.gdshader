shader_type spatial;
render_mode diffuse_burley, specular_schlick_ggx, cull_back;

// Opaque depth-buffered paper with Godot's inexpensive backlighting term.
// This is NOT ray-traced transmission/refraction, alpha transparency or emission.
uniform vec4 paper_color : source_color = vec4(0.83, 0.75, 0.60, 1.0);
uniform vec4 backlight_color : source_color = vec4(0.70, 0.58, 0.39, 1.0);
uniform float backlight_strength : hint_range(0.0, 1.0) = 0.35;
uniform float fibre_scale : hint_range(20.0, 600.0) = 300.0;
uniform float grain_amount : hint_range(0.0, 0.15) = 0.055;
varying vec3 local_position;

float hash31(vec3 p) {
    p = fract(p * vec3(0.1031, 0.1030, 0.0973));
    p += dot(p, p.yxz + 33.33);
    return fract((p.x + p.y) * p.z);
}

float soft_noise(vec3 p) {
    vec3 i = floor(p);
    vec3 f = fract(p);
    f = f*f*(3.0-2.0*f);
    return mix(mix(mix(hash31(i), hash31(i+vec3(1,0,0)),f.x),
                   mix(hash31(i+vec3(0,1,0)),hash31(i+vec3(1,1,0)),f.x),f.y),
               mix(mix(hash31(i+vec3(0,0,1)),hash31(i+vec3(1,0,1)),f.x),
                   mix(hash31(i+vec3(0,1,1)),hash31(i+vec3(1,1,1)),f.x),f.y),f.z);
}

void vertex() {
    local_position = VERTEX;
}

void fragment() {
    float fibre = soft_noise(local_position * fibre_scale);
    ALBEDO = paper_color.rgb * (1.0 + (fibre - 0.5) * grain_amount);
    ROUGHNESS = 0.88;
    SPECULAR = 0.16;
    BACKLIGHT = backlight_color.rgb * backlight_strength;
}
