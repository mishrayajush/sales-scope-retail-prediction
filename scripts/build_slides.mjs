// Rebuild with the Codex bundled artifact runtime. Pass its package root through
// ARTIFACT_NODE_MODULES when running outside the preconfigured Codex environment.
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const root=path.resolve(import.meta.dirname,'..');
const runtime=process.env.ARTIFACT_NODE_MODULES ?? 'C:/Users/YaM/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
process.env.RUNTIME_NODE_MODULES=runtime;
const {Presentation,PresentationFile}=await import(pathToFileURL(path.join(runtime,'@oai/artifact-tool/dist/artifact_tool.mjs')).href).catch(async()=>{
 const pkg=JSON.parse(await fs.readFile(path.join(runtime,'@oai/artifact-tool/package.json'),'utf8'));
 return import(pathToFileURL(path.join(runtime,'@oai/artifact-tool',pkg.main)).href);
});
let m=null;
try {m=JSON.parse(await fs.readFile(path.join(root,'artifacts/metrics.json'),'utf8'));}catch{}
const presentation=Presentation.create({slideSize:{width:1280,height:720}});
const slides=[
 ['Retail Sales Prediction',['Capstone Project 2','Daily store sales forecasting','DRAFT: '+(m?'measured run available, student review required':'data and measured results pending')]],
 ['Problem and practical use',['Predict one known store’s daily sales from information available before the day.','Use estimates to support inventory and staffing discussions.','Target: continuous, nonnegative sales in dataset units.']],
 ['Rossmann dataset',['Use train.csv and store.csv from the Kaggle competition.','Calendar, store, promotion and holiday features inform predictions.','Exclude same-day Customers to avoid unavailable future information.']],
 ['Data preparation and EDA',['Validate store/date keys, labels, schedules and metadata joins.','Fit numeric imputation and encoding on training observations.','Review training-period trend, weekday, promotion and store-type charts.','Promotion comparisons show associations. They do not establish causality.']],
 ['Models and time separation',['Compare Ridge regression and Random Forest with store/weekday mean sales.','Reserve the last 42 days for test and the previous 42 for validation.','Select by validation MAE, refit on train plus validation, then score test once.','Train on open days and return zero for planned closures.']],
 ['Evaluation and results',m ? [`Selected method: ${m.selected_model}`,`Test MAE: ${m.test.all.MAE.toFixed(2)}    RMSE: ${m.test.all.RMSE.toFixed(2)}`,`Open-day MAE: ${m.test.open.MAE.toFixed(2)}    R²: ${m.test.open.R2?.toFixed(3)}`,`Scope: ${m.scope}`] : ['Real-data training and test evaluation remain pending.','Report MAE, RMSE and R² for all days and open days.','Compare validation results with the baseline before selecting a method.','Synthetic software tests do not establish forecasting accuracy.']],
 ['Streamlit application',['Inputs: known store, future date, opening plan, promotion and holidays.','The app reuses the saved preprocessing and prediction method.','Reject unknown stores and invalid inputs. Warn beyond the tested horizon.','Public deployment pending authenticated GitHub and Streamlit setup.']],
 ['Limitations and future work',['Historical store patterns may drift. Distant forecasts remain unverified.','One time holdout provides limited evidence across forecast origins.','Compare rolling-origin validation, safely shifted lags and boosted trees.','Complete the measured findings and verified app URL before submission.']]
];
function text(slide,value,left,top,width,height,size,color,bold=false){
 const box=slide.shapes.add({geometry:'textbox',position:{left,top,width,height},fill:'none',line:{fill:'none',width:0}});
 box.text=value;box.text.style={typeface:'Arial',fontSize:size,color,bold};
}
for(const [i,[title,body]] of slides.entries()){
 const slide=presentation.slides.add();slide.background.fill='#F6F4EF';
 slide.speakerNotes.text='Sources: https://www.kaggle.com/c/rossmann-store-sales/data ; https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html ; https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app . '+(m?'Metrics: local artifacts/metrics.json.':'Real-data analysis pending.');
 text(slide,title,80,65,1120,105,i===0?58:44,'#173F4F',true);
 body.forEach((line,j)=>text(slide,line,84,210+j*100,1090,88,28,'#273846'));
 text(slide,`${i+1} / 8`,1120,665,90,28,16,'#607080');
}
const build=path.join(root,'.build/slides');
await fs.mkdir(build,{recursive:true});await fs.mkdir(path.join(root,'output/presentation'),{recursive:true});
for(const [i,slide] of presentation.slides.items.entries()){
 const image=await presentation.export({slide,format:'png',scale:1});
 await fs.writeFile(path.join(build,`slide-${i+1}.png`),new Uint8Array(await image.arrayBuffer()));
}
const candidate=path.join(build,'candidate.pptx');
await (await PresentationFile.exportPptx(presentation)).save(candidate);
const skill=process.env.PRESENTATION_SKILL_DIR ?? 'C:/Users/YaM/.codex/plugins/cache/openai-primary-runtime/presentations/26.1013.11914/skills/presentations';
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
let finalPath=path.join(root,'output/presentation/Retail_Sales_Presentation_DRAFT.pptx');
try {await fs.access(finalPath);finalPath=path.join(root,`output/presentation/Retail_Sales_Presentation_DRAFT_${Date.now()}.pptx`);}catch{}
const result=await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath,pythonExecutable:process.env.RUNTIME_PYTHON ?? 'C:/Users/YaM/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit'],explicitTotalSlideCount:8,fontPolicy:{basis:'design',families:['Arial']},verifyArtifactToolImport:true,receiptPath:path.join(build,'validation.json')});
console.log(result);
