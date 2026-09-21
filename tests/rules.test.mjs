import test from 'node:test';
import assert from 'node:assert/strict';
import {evaluate,initialConfig,assessPerformance,catalog,selected,physicalRules} from '../dist/data.js';
import {analyzeMeasurements} from '../dist/measurements.js';
import {assistantContext,guideAnswer} from '../dist/assistant.js';
import {extractSpecifications,normalizePart} from '../dist/specifications.js';
test('coincidencias parciales nunca confirman el equipo completo',()=>{
 const r=evaluate(initialConfig);assert.equal(r.filter(x=>x.status==='pass').length,11);assert.equal(r.at(-1).status,'unknown');
});
test('CPU Intel en placa AM5 y DDR4 producen incompatibilidades independientes',()=>{
 const r=evaluate({...initialConfig,cpu:'intelcpu',ram:'ddr4'});assert.equal(r[0].status,'fail');assert.equal(r[1].status,'fail');
});
test('se aplica el menor límite de RAM entre CPU y motherboard',()=>{
 assert.equal(catalog.board.options[0].maxRam,192);assert.equal(evaluate({...initialConfig,ram:'large5'})[2].status,'fail');
});
test('M.2 SATA es incompatible con ASUS, pero MSI lo permite con restricción de puerto',()=>{
 assert.equal(evaluate({...initialConfig,ssd:'sata'})[3].status,'fail');
 const r=evaluate({...initialConfig,board:'intel',cpu:'intelcpu',ram:'ddr4',ssd:'sata'});assert.equal(r[3].status,'pass');assert.match(r[3].detail,/M2_2/);assert.match(r[3].detail,/SATA8/);
});
test('no se analiza rendimiento de una configuración incompatible',()=>{
 const r=assessPerformance({...initialConfig,cpu:'intelcpu'},'visual');assert.equal(r.items.length,0);assert.match(r.title,/incompatibilidades/);
});
test('el análisis cambia con el uso sin inventar mediciones',()=>{
 const a=assessPerformance(initialConfig,'visual'),b=assessPerformance(initialConfig,'competitive');assert.notEqual(a.items[1].text,b.items[1].text);assert.match(a.detail,/No hay benchmarks/);
});
test('entradas desconocidas se rechazan',()=>{
 assert.throws(()=>evaluate({...initialConfig,gpu:'inventada'}));assert.throws(()=>assessPerformance(initialConfig,'desconocido'));
});
test('fuente desconocida produce información pendiente, nunca aprobación',()=>{
 const results=evaluate({...initialConfig,psu:'psu-unknown'});for(const r of results.filter(r=>/fuente|Potencia|Conectores/.test(r.name)))assert.equal(r.status,'unknown');
});
test('límites físicos y cables se comprueban independientemente',()=>{
 const parts=structuredClone(selected(initialConfig));parts.case.gpuMax=190;parts.case.coolerMax=150;parts.psu.watts=450;parts.psu.pcie8=0;
 const r=physicalRules(parts);for(const name of ['Largo de la GPU','Altura del cooler','Potencia recomendada por fabricante de GPU','Conectores de alimentación'])assert.equal(r.find(x=>x.name===name).status,'fail');
});
const capture=(overrides={})=>Array.from({length:40},()=>({fps:60,gpu:98,cpuMax:70,ram:60,vram:65,...overrides}));
test('mediciones distinguen GPU, CPU y límite de FPS',()=>{
 assert.match(analyzeMeasurements(capture()).findings[0],/límite de GPU/);
 assert.match(analyzeMeasurements(capture({gpu:50,cpuMax:96})).findings[0],/límite de CPU/);
 const capped=analyzeMeasurements(capture(),{fpsCap:true});assert.ok(!capped.findings.some(s=>s.startsWith('Posible límite')));
});
test('mediciones inválidas no generan diagnósticos',()=>{
 for(const data of [[],capture({gpu:101}),capture({fps:NaN}),capture({cpuMax:null}),capture().slice(0,29)])assert.throws(()=>analyzeMeasurements(data));
});
test('asistente recibe alertas del motor y cambia según paso',()=>{
 assert.equal(assistantContext(initialConfig,2).title,'Instalá la memoria');
 assert.ok(assistantContext({...initialConfig,cpu:'intelcpu'},0).rules.some(r=>r.status==='fail'));
 assert.match(guideAnswer('¿Puedo forzar si no entra?',initialConfig,1),/Detené/);
 assert.match(guideAnswer('SSD SATA',{...initialConfig,board:'intel',cpu:'intelcpu',ram:'ddr4',ssd:'sata'},3),/SATA8/);
});
test('extracción de medidas maneja coma decimal y rechaza contradicciones',()=>{
 assert.deepEqual(extractSpecifications('gpu','Largo: 240 mm\nEspesor: 44,07 mm'),{length:240,thickness:44.07});
 assert.throws(()=>extractSpecifications('gpu','Largo: 200 mm\nLength: 240 mm'));
});
test('fichas nuevas requieren medidas y procedencia válidas',()=>{
 const fields={length:199,thickness:41,minPsu:550,pcie8:1,vram:8};
 assert.equal(normalizePart('gpu','GPU ejemplo','https://example.com/spec',fields).provided,true);
 assert.throws(()=>normalizePart('gpu','GPU ejemplo','javascript:alert(1)',fields));
 assert.throws(()=>normalizePart('gpu','<img src=x>','https://example.com',fields));
 assert.throws(()=>normalizePart('gpu','GPU ejemplo','https://example.com',{...fields,length:undefined}));
 assert.throws(()=>normalizePart('gpu','GPU ejemplo','https://example.com',{...fields,pcie8:1.5}));
});
