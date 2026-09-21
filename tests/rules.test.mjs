import test from 'node:test';
import assert from 'node:assert/strict';
import {evaluate,initialConfig,assessPerformance,catalog} from '../dist/data.js';
test('coincidencias parciales nunca confirman el equipo completo',()=>{
 const r=evaluate(initialConfig);assert.equal(r.filter(x=>x.status==='pass').length,4);assert.equal(r.at(-1).status,'unknown');
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
