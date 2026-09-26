#version 140

in mediump vec2 var_texcoord0;
out vec4 color_out;
uniform lowp sampler2D texture_sampler;
uniform fs_uniforms
{
    lowp vec4 tint;
};

void main()
{
    vec4 tint_pm = vec4(tint.xyz * tint.w, tint.w);
    color_out = texture(texture_sampler, var_texcoord0) * tint_pm;
}
