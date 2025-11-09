// **** WEAPON ROTATION SHADER ****
// Contributors: SinsOfSeven, Silent, DiXiao
struct VertexAttributes {
  float3 position;//12
  float3 normal;//24
  float4 tangent;//40
};

RWStructuredBuffer<VertexAttributes> rw_buffer : register(u0);
StructuredBuffer<VertexAttributes> base : register(t0);
StructuredBuffer<VertexAttributes> shapekey : register(t1);

Texture1D<float4> IniParams : register(t120);
#define rotation IniParams[0]
#define offset IniParams[1]

float2 uintToHalf2ToFloat2(in uint a){
  return float2(f16tof32(a.x & 0xffff), f16tof32(a.x >> 0x10 & 0xffff));
}

uint float2ToHalf2ToUint(in float2 a){
  return uint(asuint(f32tof16(a.x)) | asuint(f32tof16(a.y)) << 0x10);
}

float3 RotateVector(float3 p, float3 a, float3 o)
{ //Thanky DiXiao and Silent
    p = p - o;
    float3x3 rotationMatrix = float3x3(
        cos(a.y) * cos(a.z), 
        sin(a.x) * sin(a.y) * cos(a.z) - cos(a.x) * sin(a.z), 
        cos(a.x) * sin(a.y) * cos(a.z) + sin(a.x) * sin(a.z),

        cos(a.y) * sin(a.z), 
        sin(a.x) * sin(a.y) * sin(a.z) + cos(a.x) * cos(a.z), 
        cos(a.x) * sin(a.y) * sin(a.z) - sin(a.x) * cos(a.z),

        -sin(a.y), 
        sin(a.x) * cos(a.y), 
        cos(a.x) * cos(a.y)
    );
    return mul(p, rotationMatrix)+o;
}

[numthreads(1, 1, 1)]
void main(uint3 threadID : SV_DispatchThreadID)
{
  float4 p,a,c = float4(0,0,0,1);
  float3 o = float3(offset.xyz);
  uint i = threadID.x + rotation.w;

  a.xyz = float3(radians(rotation.x), radians(rotation.y), radians(rotation.z));
  c.xyz = RotateVector(base[i].position.xyz, a.xyz, o.xyz);
  
  rw_buffer[i].position.xyz = c.xyz;
  c.xyz = RotateVector(base[i].normal.xyz, a.xyz, o.xyz);
  rw_buffer[i].normal.xyz = c.xyz;
  c.xyz = RotateVector(base[i].tangent.xyz, a.xyz, o.xyz);
  rw_buffer[i].tangent.xyz = c.xyz;
  //rw_buffer[i].normal.xyz = float2ToHalf2ToUint(c.zw);
}