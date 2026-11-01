import fs from "node:fs";
import { chromium } from "playwright";

const results={
  source:"https://dzpage.com/en/map-editor",
  read_only:true,
  cost_type:"Github Actions / no paid browser",
  nitrado_modified:false,
  exact_elevations_extracted:0,
  screenshotted:false,
  browser_events:[],
  selected_map:null,
  select_options:[],
  visible_text:[],
  failures:[]
};
const browser=await chromium.launch({headless:true,args:["--no-sandbox","--disable-dev-shm-usage"]});
try{
  const page=await browser.newPage({viewport:{width:1440,height:900}});
  page.on("response", async r=>{
    try{
      const u=new URL(r.url());
      if(u.hostname!=="dzpage.com")return;
      const ext=u.pathname.toLowerCase();
      if(/terrain|height|enoch|livonia|\.bin|\.wasm|\.json|\.pbf|\.png|\.webp|\/tiles\//.test(ext)){
        if(results.browser_events.length<140){
          const h=r.headers();
          results.browser_events.push({url:u.pathname,query:u.search.slice(0,85),
             status:r.status(),type:h["content-type"],size:h["content-length"]||null});
        }
      }
    }catch(e){}
  });
  page.on("pageerror", e=>{
    if(results.failures.length<15)results.failures.push("pageerror: "+String(e.message).slice(0,110));
  });
  await page.goto(results.source,{waitUntil:"domcontentloaded",timeout:65000});
  await page.waitForTimeout(8000);
  results.select_options=await page.locator("select").evaluateAll(nodes=>
    nodes.map((s,i)=>({index:i,options:Array.from(s.options).map(o=>({value:o.value,text:o.textContent?.trim().slice(0,50)})).slice(0,12)})).slice(0,12)
  );
  for(const s of results.select_options){
    const opts=s.options||[];
    const opt=opts.find(x=>/livonia|enoch/i.test(x.value+" "+x.text));
    if(opt){
      try{
        await page.locator("select").nth(s.index).selectOption(opt.value);
        results.selected_map=opt;
        break;
      }catch(e){results.failures.push("select error "+String(e).slice(0,100));}
    }
  }
  await page.waitForTimeout(12000);
  results.visible_text=(await page.locator("body").innerText({timeout:8000})).split("\n").filter(v=>/livonia|enoch|height|ground|objects|terrain|loading/i.test(v)).slice(0,35);
  const dir="deploy/v25";
  fs.mkdirSync(dir,{recursive:true});
  try{await page.screenshot({path:dir+"/map_editor_runtime.png",fullPage:false});results.screenshotted=true;}catch(e){}
}catch(e){
  results.failures.push("Fatal:"+String(e).slice(0,350));
}finally{await browser.close();}
fs.mkdirSync("deploy/v25",{recursive:true});
fs.writeFileSync("deploy/v25/DZPAGE_BROWSER_PROBE.json",JSON.stringify(results,null,2)+"\n");
console.log(JSON.stringify(results,null,2));
