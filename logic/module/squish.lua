-- Pressure equilibrium plus a damped impact spring. Area-preserving rendering
-- and a small, slowly changing circular collider give a lightweight approximation.
local M = {MIN_SPEED=160,FULL_SPEED=1100,MAX_COMPRESSION=0.25,
    MAX_REBOUND=0.075,FREQUENCY=27,DAMPING_RATIO=0.34,COOLDOWN=0.09}
local function clamp(x,a,b) return math.max(a,math.min(b,x)) end
function M.new(softness)
    return {softness=softness or 0.8,amount=0,impact=0,velocity=0,
        rest=0,pressure=0,nx=0,ny=1,time=0,last_impact=-1,contacts={},
        pending_speed=0,pending_nx=0,pending_ny=1,
        xx=0,xy=0,yy=0,load_samples=0,frame_dt=1/60,body_scale=1}
end
function M.contact(s,key,nx,ny,speed,load)
    local length=math.sqrt(nx*nx+ny*ny)
    if length<0.001 then return end
    nx,ny=nx/length,ny/length
    if load and load>0 then
        load=math.min(load,24)
        s.xx=s.xx+load*nx*nx;s.xy=s.xy+load*nx*ny;s.yy=s.yy+load*ny*ny
        s.load_samples=s.load_samples+1
    end
    local previous=s.contacts[key];s.contacts[key]=s.time
    if previous and s.time-previous<=s.frame_dt*2.5 then return end
    if s.time-s.last_impact<M.COOLDOWN or speed<=M.MIN_SPEED or speed<=s.pending_speed then return end
    s.pending_speed=speed;s.pending_nx=nx;s.pending_ny=ny
end
function M.impact(s,nx,ny,speed)
    local strength=clamp((speed-M.MIN_SPEED)/(M.FULL_SPEED-M.MIN_SPEED),0,1)
    if strength==0 then return false end
    s.nx,s.ny=nx,ny
    local maximum=(0.055+0.165*s.softness)*M.FREQUENCY/0.65
    s.velocity=math.min(math.max(0,s.velocity)+strength*maximum,maximum)
    s.last_impact=s.time;return true
end
function M.update(s,dt,hold_pressure)
    if dt<=0 then return end
    dt=math.min(dt,0.5);s.time=s.time+dt;s.frame_dt=dt
    if s.pending_speed>0 then
        M.impact(s,s.pending_nx,s.pending_ny,s.pending_speed);s.pending_speed=0
    end
    local target=s.pressure
    if s.load_samples>0 then
        target=clamp(s.xx+s.yy,0,24)
        if s.time-s.last_impact>0.3 then
            local angle=0.5*math.atan2(2*s.xy,s.xx-s.yy)
            local nx,ny=math.cos(angle),math.sin(angle)
            if nx*s.nx+ny*s.ny<0 then nx,ny=-nx,-ny end
            local a=1-math.exp(-dt*5)
            s.nx,s.ny=s.nx+(nx-s.nx)*a,s.ny+(ny-s.ny)*a
            local len=math.sqrt(s.nx*s.nx+s.ny*s.ny)
            if len>0.001 then s.nx,s.ny=s.nx/len,s.ny/len end
        end
    elseif not hold_pressure then target=0 end
    s.pressure=s.pressure+(target-s.pressure)*(1-math.exp(-dt*4))
    s.xx,s.xy,s.yy,s.load_samples=0,0,0,0
    local target_rest=math.min(0.135*s.softness,0.045*s.softness*math.log(1+s.pressure))
    local rate=target_rest>s.rest and 1.8 or 3.5
    s.rest=s.rest+(target_rest-s.rest)*(1-math.exp(-dt*rate))
    local w=M.FREQUENCY*(1.2-0.3*s.softness);local d=w*M.DAMPING_RATIO
    local wd=w*math.sqrt(1-M.DAMPING_RATIO*M.DAMPING_RATIO)
    local a=s.impact;local b=(s.velocity+d*a)/wd
    local c,si=math.cos(wd*dt),math.sin(wd*dt);local e=math.exp(-d*dt)
    s.impact=e*(a*c+b*si)
    s.velocity=e*((-d*a+wd*b)*c+(-d*b-wd*a)*si)
    s.impact=clamp(s.impact,-M.MAX_REBOUND,0.23)
    if math.abs(s.impact)<0.00015 and math.abs(s.velocity)<0.006 then s.impact,s.velocity=0,0 end
    if s.rest<0.00015 and s.pressure<0.001 then s.rest=0 end
    s.amount=clamp(s.rest+s.impact,-M.MAX_REBOUND,M.MAX_COMPRESSION)
    -- At most 6.5% physical radius compression. Never scale the whole game object.
    s.body_scale=1-0.48*s.rest
    for key,last in pairs(s.contacts) do if s.time-last>0.5 then s.contacts[key]=nil end end
end
function M.scales(s) return math.exp(-s.amount),math.exp(s.amount) end
return M
