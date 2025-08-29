import L from 'leaflet';

const base = (svg: string) =>
  L.divIcon({
    className: 'pin',
    html: svg,
    iconSize: [36, 36],
    iconAnchor: [18, 36],
    popupAnchor: [0, -28],
  });

export const restaurantIcon = base(
  `<div style="filter: drop-shadow(0 4px 8px rgba(0,0,0,.25))">
     <svg width="36" height="36" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
       <path d="M18 0c7.7 0 14 6.3 14 14 0 10.5-14 22-14 22S4 24.5 4 14C4 6.3 10.3 0 18 0Z" fill="#FF8A00"/>
       <text x="18" y="20" font-size="12" text-anchor="middle" fill="white" font-weight="700">🍔</text>
     </svg>
   </div>`
);

export const customerIcon = base(
  `<div style="filter: drop-shadow(0 4px 8px rgba(0,0,0,.25))">
     <svg width="36" height="36" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
       <path d="M18 0c7.7 0 14 6.3 14 14 0 10.5-14 22-14 22S4 24.5 4 14C4 6.3 10.3 0 18 0Z" fill="#2D9CDB"/>
       <text x="18" y="20" font-size="12" text-anchor="middle" fill="white" font-weight="700">🏠</text>
     </svg>
   </div>`
);

export const captainIcon = (highlight = false) =>
  base(
    `<div style="filter:${highlight ? 'drop-shadow(0 0 10px rgba(0,255,0,.9))' : 'drop-shadow(0 4px 8px rgba(0,0,0,.25))'}">
       <svg width="36" height="36" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
         <path d="M18 0c7.7 0 14 6.3 14 14 0 10.5-14 22-14 22S4 24.5 4 14C4 6.3 10.3 0 18 0Z" fill="#27AE60"/>
         <text x="18" y="20" font-size="12" text-anchor="middle" fill="white" font-weight="700">🛵</text>
       </svg>
     </div>`
  );
