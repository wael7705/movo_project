export async function getCounters(){
  const r = await fetch("/api/v1/admin/counters");
  return r.json();
}

export async function getRestaurants(){
  const r = await fetch("/api/v1/admin/restaurants");
  return r.json();
}

export async function toggleRestaurant(id:number, visible:boolean){
  await fetch(`/api/v1/admin/restaurant/${id}/visible`,{method:"PATCH",headers:{'Content-Type':'application/json'},body:JSON.stringify({visible})});
}

export async function toggleCategory(id:number, visible:boolean){
  await fetch(`/api/v1/admin/category/${id}/visible`,{method:"PATCH",headers:{'Content-Type':'application/json'},body:JSON.stringify({visible})});
}

export async function toggleAddon(id:number, visible:boolean){
  await fetch(`/api/v1/admin/addon/${id}/visible`,{method:"PATCH",headers:{'Content-Type':'application/json'},body:JSON.stringify({visible})});
}

export async function getCaptainsLive(){
  const r = await fetch("/api/v1/admin/captains/live");
  return r.json();
}

export async function sendNotify(tab:string,message:string){
  await fetch("/api/v1/admin/notify",{method:"POST",headers:{'Content-Type':'application/json'},body:JSON.stringify({tab,message})});
}

export async function getRestaurantStats(id: number){
  const r = await fetch(`/api/v1/admin/restaurant/${id}/stats`);
  return r.json();
}


