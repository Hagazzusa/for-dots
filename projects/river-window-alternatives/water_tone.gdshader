shader_type spatial;
render_mode cull_back;
uniform vec4 base_color : source_color = vec4(0.24, 0.39, 0.43, 1.0);
varying vec2 world_xz;
float hash2(vec2 p) { return fract(sin(dot(p, vec2(127.1,311.7))) * 43758.5453); }
float field(vec2 p) {
 vec2 i = floor(p); vec2 f = fract(p); f=f*f*(3.0-2.0*f);
 return mix(mix(hash2(i),hash2(i+vec2(1,0)),f.x),mix(hash2(i+vec2(0,1)),hash2(i+vec2(1,1)),f.x),f.y);
}
void vertex() { world_xz = (MODEL_MATRIX * vec4(VERTEX,1.0)).xz; }
void fragment() {
 float n=field(world_xz/13.0)*0.72+field(world_xz/28.0+vec2(8.3,1.2))*0.28;
 float tone=mix(0.78,1.0,smoothstep(0.28,0.48,n));
 tone=mix(tone,1.16,smoothstep(0.56,0.74,n));
 ALBEDO=base_color.rgb*tone; ROUGHNESS=0.95;
}
