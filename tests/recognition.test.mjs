import test from 'node:test';
import assert from 'node:assert/strict';
import {toDisplayBoxes} from '../recognition/frontend.js';
const fixture={schemaVersion:1,image:{width:640,height:320},detections:[{classId:'CPU_SOCKET',confidence:.9,bbox:{x:10,y:20,width:100,height:60}}]};
test('UI boxes rescale without confidence',()=>{assert.deepEqual(toDisplayBoxes(fixture,320,160),[{id:0,classId:'CPU_SOCKET',x:5,y:10,width:50,height:30}]);});
test('invalid box and response are rejected',()=>{assert.throws(()=>toDisplayBoxes({},320,160));assert.throws(()=>toDisplayBoxes({...fixture,detections:[{classId:'CPU_SOCKET',bbox:{x:639,y:0,width:10,height:10}}]},320,160));});
