// Lightweight DOM harness checks calculations and filter paths, not browser layout.
const fs=require('fs'),vm=require('vm'),assert=require('assert');const elements={};
const get=id=>elements[id]||(elements[id]={value:'',innerHTML:'',textContent:'',addEventListener(){}});
const context=vm.createContext({window:{},document:{getElementById:get},Intl,console});
vm.runInContext(fs.readFileSync('docs/data.js','utf8'),context);vm.runInContext(fs.readFileSync('docs/app.js','utf8'),context);
assert(get('kpis').innerHTML.includes('99.6%'));
for(const store of ['','London Central'])for(const category of ['','Dairy'])for(const month of ['','2025-10']){
get('store').value=store;get('category').value=category;get('month').value=month;vm.runInContext('render()',context);
assert(!get('kpis').innerHTML.includes('NaN'));assert(get('recommendations').innerHTML.includes('<table>'));
}
get('category').value='Dairy';get('sku').value='SKU060';vm.runInContext('render()',context);assert(get('recommendations').innerHTML.includes('No matching'));
console.log('PASS: dashboard KPI, filter combinations, empty state, render execution. Layout not tested.');
