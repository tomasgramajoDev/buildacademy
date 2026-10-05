import test from 'node:test';
import assert from 'node:assert/strict';
import {classifyPCQuestion,pcExplanation} from '../dist/pc-advice.js';
import {initialConfig} from '../dist/data.js';
import {galleryQuery,safeCommonsImage,safeCommonsPage} from '../dist/gallery.js';
test('rendimiento usa evidencia real y respeta incompatibilidades y limite FPS',()=>{
 assert.match(pcExplanation('performance',initialConfig),/No cargaste mediciones/);
 const measurements=Array.from({length:30},()=>({fps:60,gpu:99,cpuMax:40,ram:40,vram:40}));
 assert.match(pcExplanation('performance',initialConfig,{measurements}),/Posible límite de GPU/);
 assert.doesNotMatch(pcExplanation('performance',initialConfig,{measurements,fpsCap:true}),/Posible límite de GPU/);
 assert.match(pcExplanation('performance',{...initialConfig,cpu:'intelcpu'},{measurements}),/Primero resolvé/);
});
test('consulta de rendimiento no se confunde con montaje de RAM y limita temas',()=>{
 assert.equal(classifyPCQuestion('¿Mi RAM causa un cuello de botella?'),'performance');
 assert.equal(classifyPCQuestion('¿Qué es la RAM?'),'basics');
 assert.equal(classifyPCQuestion('¿Por qué?','performance'),'performance');
 assert.equal(classifyPCQuestion('Escribime una receta de torta'),'unknown');
 assert.equal(classifyPCQuestion('No entra el procesador'),'care');
});
test('galeria consulta Commons sin aceptar hosts o protocolos externos',()=>{
 assert.equal(safeCommonsImage('https://thumb.wikimedia.org/a.jpg'),true);
 for(const url of ['http://upload.wikimedia.org/a','https://thumb.wikimedia.org.evil.test/a','javascript:alert(1)','https://user:pass@upload.wikimedia.org/a'])assert.equal(safeCommonsImage(url),false);
 assert.equal(safeCommonsPage('https://commons.wikimedia.org/wiki/File:Board.jpg'),true);
 const url=new URL(galleryQuery('ASUS " OR secret:',18));assert.equal(url.searchParams.get('gsroffset'),'18');assert.ok(!url.searchParams.get('gsrsearch').includes('secret:'));
});
