import test from 'node:test';
import assert from 'node:assert/strict';
import {parseIntent,answerForTopic,topics} from '../dist/assistant.js';
import {initialConfig} from '../dist/data.js';
test('salida del modelo solo selecciona temas permitidos, nunca instrucciones libres',()=>{
 assert.equal(parseIntent('{"topic":"planning","advice":"Inventar un voltaje"}'),'planning');
 for(const text of ['{"topic":"inventar"}','null','Texto libre'])assert.throws(()=>parseIntent(text));
 assert.match(answerForTopic('planning',initialConfig,0),/ocho pasos/);
});
test('cada tema produce contenido del proyecto y respeta configuración incompatible',()=>{
 for(const topic of topics)assert.ok(answerForTopic(topic,initialConfig,0).length>30);
 assert.match(answerForTopic('compatibility',{...initialConfig,cpu:'intelcpu'},0),/socket/i);
 assert.match(answerForTopic('manual',initialConfig,0),/ASUS/);
 assert.match(answerForTopic('care',initialConfig,0),/no lo fuerces/);
});
