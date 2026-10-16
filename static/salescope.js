const root=document.documentElement;
const toggle=document.querySelector('#theme-toggle');
function setTheme(dark){root.dataset.theme=dark?'dark':'light';toggle.setAttribute('aria-pressed',String(dark));toggle.setAttribute('aria-label',dark?'Switch to light mode':'Switch to dark mode');document.querySelector('#theme-label').textContent=dark?'Light mode':'Dark mode';try{localStorage.setItem('salescope-theme',dark?'dark':'light');}catch{}}
let saved='light';try{saved=localStorage.getItem('salescope-theme')||'light';}catch{}
setTheme(saved==='dark');toggle.addEventListener('click',()=>setTheme(root.dataset.theme!=='dark'));
const form=document.querySelector('#forecast-form');
if(form){
const storeInput=document.querySelector('#store');
const storeIds=JSON.parse(document.querySelector('#store-ids').textContent);
const suggestions=document.querySelector('#store-suggestions');
let matches=[],active=-1;
const sampleNames=['Ice cream store','Grocery store','Clothing store','Bakery','Stationery store','General store','Bookshop','Flower shop'];
const categorySelect=document.querySelector('#category');
const categoryStore=document.querySelector('#category-store');
const storeCategory=id=>sampleNames[(id-1)%sampleNames.length];
const branchName=id=>`Store ${id} (${sampleNames[(id-1)%sampleNames.length]})`;
for(const name of sampleNames.filter(name=>storeIds.some(id=>storeCategory(id)===name))){const option=document.createElement('option');option.value=name;option.textContent=name;categorySelect.append(option);}
function populateCategory(selectedId){
 const filtered=storeIds.filter(id=>storeCategory(id)===categorySelect.value);
 categoryStore.replaceChildren();const placeholder=document.createElement('option');placeholder.value='';placeholder.textContent=categorySelect.value?'Select a store':'Select a category first';categoryStore.append(placeholder);
 for(const id of filtered){const option=document.createElement('option');option.value=String(id);option.textContent=branchName(id);categoryStore.append(option);}
 categoryStore.disabled=!categorySelect.value;
 if(filtered.includes(selectedId))categoryStore.value=String(selectedId);
 document.querySelector('#category-count').textContent=categorySelect.value?`${filtered.length} available stores · Select one to view its history`:'Choose a category to browse its stores.';
}
function syncCategory(id){categorySelect.value=storeCategory(id);populateCategory(id);}
categorySelect.addEventListener('change',()=>populateCategory(resolvedStore()));
categoryStore.addEventListener('change',()=>{if(categoryStore.value)chooseStore(Number(categoryStore.value));});
function resolvedStore(){const query=storeInput.value.trim();return /^\d{1,4}$/.test(query)?storeIds.find(id=>id===Number(query)):storeIds.find(id=>branchName(id).toLowerCase()===query.toLowerCase());}
function closeSuggestions(){suggestions.hidden=true;storeInput.setAttribute('aria-expanded','false');storeInput.removeAttribute('aria-activedescendant');active=-1;}
function validateStore(){const valid=resolvedStore()!==undefined;storeInput.setCustomValidity(valid?'':'Choose a specific store from the suggestions, or enter its number.');return valid;}
function publishStore(){const id=resolvedStore();document.dispatchEvent(new CustomEvent('salescope:store',{detail:{id:id??null,label:id===undefined?'':branchName(id)}}));if(!document.querySelector('#filled-result').hidden)document.querySelector('#stale-note').hidden=false;}
function chooseStore(id){storeInput.value=branchName(id);validateStore();syncCategory(id);closeSuggestions();storeInput.dispatchEvent(new Event('input',{bubbles:true}));document.querySelector('#store-help').textContent=`Selected: ${branchName(id)}`;closeSuggestions();}
function showSuggestions(){
 const query=storeInput.value.trim().toLowerCase();
 const matching=storeIds.filter(id=>/^\d+$/.test(query)?String(id).startsWith(query):branchName(id).toLowerCase().includes(query));matches=matching.slice(0,8);active=-1;suggestions.replaceChildren();
 for(const id of matches){const option=document.createElement('button');option.type='button';option.id=`branch-option-${id}`;option.setAttribute('role','option');option.setAttribute('aria-selected','false');option.tabIndex=-1;option.textContent=branchName(id);option.addEventListener('pointerdown',event=>event.preventDefault());option.addEventListener('click',()=>chooseStore(id));suggestions.append(option);}
 const hint=document.createElement('p');hint.className='search-hint';hint.textContent=matching.length?`${matching.length} matching stores${matching.length>8?' · Keep typing to narrow the list':''}`:'No matching store. Try a store number or an example name such as ice cream.';suggestions.append(hint);
 suggestions.hidden=false;storeInput.setAttribute('aria-expanded','true');storeInput.removeAttribute('aria-activedescendant');
}
function activate(index){active=(index+matches.length)%matches.length;for(const [i,option] of [...suggestions.querySelectorAll('[role=option]')].entries())option.setAttribute('aria-selected',String(i===active));storeInput.setAttribute('aria-activedescendant',`branch-option-${matches[active]}`);}
storeInput.addEventListener('focus',showSuggestions);
storeInput.addEventListener('input',()=>{validateStore();const id=resolvedStore();if(id!==undefined)syncCategory(id);document.querySelector('#store-help').textContent='Search all stores by number or example name.';showSuggestions();publishStore();});
storeInput.addEventListener('blur',closeSuggestions);
storeInput.addEventListener('keydown',event=>{
 if(event.key==='Escape'){closeSuggestions();return;}
 if(['ArrowDown','ArrowUp'].includes(event.key)){event.preventDefault();if(suggestions.hidden)showSuggestions();if(matches.length)activate(active<0?(event.key==='ArrowDown'?0:matches.length-1):active+(event.key==='ArrowDown'?1:-1));}
 if(event.key==='Enter'&&!suggestions.hidden){event.preventDefault();if(active>=0)chooseStore(matches[active]);else if(validateStore())closeSuggestions();}
});
if(resolvedStore()!==undefined){const id=resolvedStore();storeInput.value=branchName(id);syncCategory(id);}
validateStore();
publishStore();
let hasResult=false;
const button=document.querySelector('#predict-button');
const error=document.querySelector('#form-error');
form.addEventListener('input',()=>{if(hasResult)document.querySelector('#stale-note').hidden=false;});
form.addEventListener('submit',async event=>{
event.preventDefault();validateStore();closeSuggestions();if(!form.reportValidity())return;
button.disabled=true;button.querySelector('span').textContent='Estimating sales…';error.hidden=true;
try{
const payload={store:resolvedStore(),date:form.elements.date.value,open:form.elements.open.checked,promo:form.elements.promo.checked,holiday:form.elements.holiday.value,school_holiday:form.elements.school.checked};
const response=await fetch('/api/predict',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
const result=await response.json();if(!response.ok)throw new Error(result.error||'Could not calculate the estimate. Please try again.');
document.querySelector('#empty-result').hidden=true;document.querySelector('#filled-result').hidden=false;
document.querySelector('#result-state').textContent='Estimate ready';
document.querySelector('#result-value').textContent=new Intl.NumberFormat('en',{minimumFractionDigits:2,maximumFractionDigits:2}).format(result.value);
const displayDate=new Date(`${result.date}T12:00:00`).toLocaleDateString('en-GB',{day:'numeric',month:'long',year:'numeric'});
document.querySelector('#result-context').textContent=`${branchName(result.store)} · ${displayDate}`;
document.querySelector('#result-explanation').textContent=result.opened?'Based on the store’s historical patterns and the plans you selected.':'The store is closed on this date, so estimated sales are zero.';
const holidayNames={'0':'No public holiday',a:'Public holiday',b:'Easter',c:'Christmas'};
document.querySelector('#scenario').textContent=`Store ${result.opened?'open':'closed'} · ${result.promo?'Promotion planned':'No promotion'} · ${holidayNames[result.holiday]}${result.school_holiday?' · School holiday':''}`;
document.querySelector('#horizon-warning').hidden=!result.outside_horizon;document.querySelector('#stale-note').hidden=true;hasResult=true;
if(matchMedia('(max-width:760px)').matches)document.querySelector('.result-panel').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'instant':'smooth',block:'start'});
}catch(issue){error.textContent=issue.message||'Could not reach the model. Please check that the server is running.';error.hidden=false;if(hasResult)document.querySelector('#stale-note').hidden=false;}
finally{button.disabled=false;button.querySelector('span').textContent='Estimate daily sales';}
});
}
