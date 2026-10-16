(()=>{
const chart=document.querySelector('#history-chart');if(!chart)return;
const status=document.querySelector('#history-status'),range=document.querySelector('#history-range'),tbody=document.querySelector('#history-table-body');
const tabs=[...document.querySelectorAll('[data-period]')];
let store=null,label='',period='week',timer,controller,sequence=0;
const cache=new Map(),fmt=new Intl.NumberFormat('en',{maximumFractionDigits:0}),ns='http://www.w3.org/2000/svg';
const displayDate=(value,options={day:'numeric',month:'short',year:'numeric'})=>new Date(`${value}T00:00:00Z`).toLocaleDateString('en-GB',{...options,timeZone:'UTC'});
function periodLabel(p){let text=period==='year'?p.start.slice(0,4):period==='month'?displayDate(p.start,{month:'short',year:'numeric'}):`${displayDate(p.start,{day:'numeric',month:'short'})} – ${displayDate(p.end)}`;return text+(p.partial?' *':'');}
function svgNode(tag,attributes={},text){const element=document.createElementNS(ns,tag);for(const [key,value]of Object.entries(attributes))element.setAttribute(key,String(value));if(text!==undefined)element.textContent=text;return element;}
function render(data){
 chart.replaceChildren();tbody.replaceChildren();
 range.textContent=`${label} · ${displayDate(data.start)} to ${displayDate(data.end)} · Training-period observations only`;
 document.querySelector('#history-title').textContent=`${{week:'Weekly',month:'Monthly',year:'Yearly'}[period]} sales history`;
 status.textContent='';status.hidden=true;chart.setAttribute('aria-busy','false');
 const points=data.points,values=points.filter(p=>p.sales!==null).map(p=>p.sales);
 const width=1000,height=300,pad={left:70,right:20,top:22,bottom:42},plotWidth=width-pad.left-pad.right,plotHeight=height-pad.top-pad.bottom;
 const max=Math.max(...values,1)*1.12,x=i=>pad.left+(points.length===1?plotWidth/2:i/(points.length-1)*plotWidth),y=value=>pad.top+(1-value/max)*plotHeight;
 const svg=svgNode('svg',{viewBox:`0 0 ${width} ${height}`,role:'img','aria-label':`${label}: actual total sales by ${period}. Exact values are available in the sales figures table below.`});
 svg.append(svgNode('title',{},`${label} — actual historical sales`));
 for(let i=0;i<=4;i++){const value=max*i/4,yy=y(value);svg.append(svgNode('line',{x1:pad.left,x2:width-pad.right,y1:yy,y2:yy,class:'chart-grid'}));svg.append(svgNode('text',{x:pad.left-12,y:yy+4,'text-anchor':'end',class:'chart-tick'},value>=1000?`${(value/1000).toFixed(value>=100000?0:1)}k`:fmt.format(value)));}
 let path='',previous=false;
 points.forEach((p,i)=>{if(p.sales===null){previous=false;return;}path+=`${previous?'L':'M'}${x(i).toFixed(2)},${y(p.sales).toFixed(2)} `;previous=true;});
 svg.append(svgNode('path',{d:path,class:'chart-line',fill:'none'}));
 const readout=document.createElement('p');readout.className='chart-readout';readout.textContent='Hover over a point for its sales total. Periods with missing days are marked *.';
 points.forEach((p,i)=>{
 const tr=document.createElement('tr');for(const value of [periodLabel(p),p.sales===null?'No observations':fmt.format(p.sales),String(p.days)]){const td=document.createElement('td');td.textContent=value;tr.append(td);}tbody.append(tr);
 if(p.sales===null)return;
 const detail=`${periodLabel(p)}: ${fmt.format(p.sales)} sales units across ${p.days} recorded days${p.partial?' (partial period)':''}`;
 const dot=svgNode('circle',{cx:x(i),cy:y(p.sales),r:period==='week'?3:5,class:p.partial?'chart-dot partial':'chart-dot'});dot.append(svgNode('title',{},detail));dot.addEventListener('pointerenter',()=>{readout.textContent=detail;});svg.append(dot);
 });
 const ticks=[...new Set(Array.from({length:Math.min(points.length,6)},(_,i)=>Math.round(i*(points.length-1)/Math.max(Math.min(points.length,6)-1,1))))];
 for(const i of ticks){const p=points[i];let text=period==='year'?p.start.slice(0,4):displayDate(p.start,{month:'short',year:'2-digit'});if(p.partial)text+=' *';svg.append(svgNode('text',{x:x(i),y:height-13,'text-anchor':i===0?'start':i===points.length-1?'end':'middle',class:'chart-tick'},text));}
 chart.append(svg,readout);
}
async function load(){
 const current=++sequence;if(controller)controller.abort();
 chart.replaceChildren();tbody.replaceChildren();status.hidden=false;chart.setAttribute('aria-busy','true');
 if(store===null){status.textContent='Select a store from the suggestions to see its history.';range.textContent='No prediction date is needed.';chart.setAttribute('aria-busy','false');return;}
 status.textContent='Loading actual sales…';const key=`${store}:${period}`;
 try{let data=cache.get(key);if(!data){controller=new AbortController();const response=await fetch(`/api/history?store=${store}&period=${period}`,{signal:controller.signal});data=await response.json();if(!response.ok)throw new Error(data.error||'Could not load history.');cache.set(key,data);}if(current!==sequence)return;render(data);}
 catch(error){if(error.name==='AbortError'||current!==sequence)return;status.textContent=error.message||'Could not load sales history. Try selecting the store again.';chart.setAttribute('aria-busy','false');}
}
document.addEventListener('salescope:store',event=>{store=event.detail.id;label=event.detail.label;document.querySelector('#prediction-store').textContent=store===null?'Choose a store above to make a prediction.':`Prediction for ${label}`;clearTimeout(timer);sequence++;if(controller)controller.abort();chart.replaceChildren();tbody.replaceChildren();range.textContent=store===null?'Choose a store to see its history.':`${label} · Loading its history`;status.hidden=false;status.textContent=store===null?'Select a matching store to continue.':'Loading actual sales…';timer=setTimeout(load,200);});
for(const tab of tabs)tab.addEventListener('click',()=>{period=tab.dataset.period;for(const item of tabs)item.setAttribute('aria-pressed',String(item===tab));clearTimeout(timer);load();});
})();
