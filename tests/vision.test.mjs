import test from 'node:test';
import assert from 'node:assert/strict';
import {decodeYOLO} from '../dist/vision.js';
const transform={width:1280,height:640,scale:.5,padX:0,padY:160};
test('deshacer letterbox mantiene cajas en coordenadas de la foto',()=>{
 const boxes=decodeYOLO(new Float32Array([320,320,100,100,.9]),[1,5,1],['CPU_SOCKET'],transform);
 assert.equal(boxes.length,1);assert.equal(boxes[0].x,540);assert.equal(boxes[0].y,220);assert.equal(boxes[0].w,200);
});
test('NMS elimina duplicados de una clase y conserva otra',()=>{
 const data=new Float32Array([320,321,320,320,320,320,100,100,100,100,100,100,.9,.8,.1,.1,.1,.85]);
 assert.equal(decodeYOLO(data,[1,6,3],['CPU_SOCKET','DIMM_SLOT'],transform).length,2);
});
test('confianza baja y salidas con forma inválida no producen detecciones',()=>{
 assert.equal(decodeYOLO(new Float32Array([320,320,100,100,.2]),[1,5,1],['CPU_SOCKET'],transform).length,0);
 assert.throws(()=>decodeYOLO(new Float32Array(5),[1,6,1],['CPU_SOCKET'],transform));
});
