import * as THREE from 'three';
import {OrbitControls} from './vendor/OrbitControls.js';

export function createScene(host){
 const scene=new THREE.Scene();scene.background=new THREE.Color('#111e20');scene.fog=new THREE.Fog('#111e20',19,40);
 const renderer=new THREE.WebGLRenderer({antialias:true,alpha:false});renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.outputColorSpace=THREE.SRGBColorSpace;host.appendChild(renderer.domElement);
 const camera=new THREE.PerspectiveCamera(38,1,.1,80);const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.minDistance=7;controls.maxDistance=23;controls.maxPolarAngle=Math.PI*.48;controls.target.set(0,.3,0);
 function reset(){camera.position.set(8,10,9);controls.target.set(0,.3,0);controls.update()}reset();
 scene.add(new THREE.HemisphereLight(0xc4e6dc,0x26382f,2.7));const key=new THREE.DirectionalLight(0xfff3dc,3.5);key.position.set(3,9,4);key.castShadow=true;key.shadow.mapSize.set(2048,2048);key.shadow.camera.left=-8;key.shadow.camera.right=8;key.shadow.camera.top=8;key.shadow.camera.bottom=-8;key.shadow.bias=-.001;scene.add(key);const rim=new THREE.DirectionalLight(0x9cdc9d,2);rim.position.set(-5,3,-4);scene.add(rim);
 const base=new THREE.Mesh(new THREE.PlaneGeometry(70,70),new THREE.MeshStandardMaterial({color:0x152326,roughness:1}));base.rotation.x=-Math.PI/2;base.position.y=-.65;base.receiveShadow=true;scene.add(base);const grid=new THREE.GridHelper(40,80,0x31403f,0x253635);grid.position.y=-.64;scene.add(grid);
 const root=new THREE.Group();scene.add(root);const groups={};const anchors={};
 function mat(color,metalness=.1){return new THREE.MeshStandardMaterial({color,metalness,roughness:.52})}
 const green=mat(0x1d5750),black=mat(0x202829),dark=mat(0x303c3d),silver=mat(0xb4bdb7,.75),gold=mat(0xbda467,.65),lime=mat(0xaadb77,.3);
 function box(parent,w,h,d,x,y,z,material){let m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),material);m.position.set(x,y,z);m.castShadow=true;m.receiveShadow=true;parent.add(m);return m}
 function cylinder(parent,r,h,x,y,z,material){let m=new THREE.Mesh(new THREE.CylinderGeometry(r,r,h,24),material);m.position.set(x,y,z);m.castShadow=true;parent.add(m);return m}
 function group(name){let g=new THREE.Group();groups[name]=g;root.add(g);return g}
 const board=group('board');box(board,5.4,.14,6.5,0,0,0,green);
 // Functional simplified board geometry: connectors, retention parts, traces and standoffs.
 for(let x=-2.5;x<2.6;x+=.42){box(board,.018,.006,5.9,x,.076,0,mat(0x31685b));}
 for(let z=-3;z<3.2;z+=.46){box(board,4.95,.006,.013,0,.079,z,mat(0x30665a));}
 for(const [x,z] of [[-2.4,-2.9],[2.4,-2.9],[-2.4,2.9],[2.4,2.9],[-2.4,0],[2.4,0]]){cylinder(board,.1,.035,x,.1,z,gold);cylinder(board,.045,.04,x,.12,z,black)}
 box(board,1.65,.14,1.65,-.45,.15,-1.2,silver);box(board,1.4,.035,1.4,-.45,.24,-1.2,black);for(let i=0;i<9;i++)for(let j=0;j<9;j++)cylinder(board,.021,.02,-1.04+i*.147,.27,-1.79+j*.147,gold);
 for(let i=0;i<4;i++){const x=1.12+i*.32;box(board,.19,.24,2.9,x,.18,-1.17,black);box(board,.035,.012,2.6,x,.309,-1.17,gold);for(const z of [-2.68,.34])box(board,.23,.25,.15,x,.21,z,silver)}
 for(const z of [1,2.45]){box(board,3.5,.23,.21,-.4,.18,z,black);box(board,3.23,.012,.032,-.4,.3,z,gold);box(board,.22,.28,.33,1.41,.2,z,silver)}
 box(board,.85,.24,.2,-1.7,.18,1.7,black);box(board,.85,.24,.2,-1.7,.18,2.9,black);
 box(board,.27,.15,.78,.9,.16,.25,black);cylinder(board,.07,.16,-1.2,.14,.25,silver);
 box(board,.38,.45,1.2,2.5,.25,-.9,black);for(let i=0;i<12;i++)box(board,.13,.04,.065,2.5,.49,-1.4+i*.09,gold);
 box(board,.65,.3,.35,-1.8,.2,-3,black);box(board,.26,.22,.32,.6,.2,-2.9,black);
 for(let i=0;i<4;i++)box(board,.4,.34,.35,2.43,.23,.7+i*.4,dark);
 for(let i=0;i<7;i++){cylinder(board,.09,.25,-1.53,.21,-2.1+i*.27,silver);box(board,.35,.25,.19,-1.95,.22,-2.1+i*.27,black)}
 for(let i=0;i<3;i++){box(board,.62,.47,.65,-2.48,.28,-2.1+i*.86,silver);box(board,.03,.23,.43,-2.8,.31,-2.1+i*.86,black)}
 box(board,1.05,.24,.95,1.2,.2,1.95,dark);for(let i=0;i<7;i++)box(board,.08,.04,.85,.8+i*.13,.34,1.95,silver);
 const cpu=group('cpu');box(cpu,1.3,.11,1.3,-.45,.32,-1.2,mat(0x567c65));box(cpu,1.17,.1,1.17,-.45,.42,-1.2,silver);box(cpu,.14,.015,.14,-.92,.478,-1.67,gold);
 const ram=group('ram');for(const x of [1.44,2.08]){box(ram,.1,.92,2.65,x,.77,-1.17,black);box(ram,.16,.14,2.73,x,1.29,-1.17,lime);for(let j=0;j<7;j++)box(ram,.135,.4,.23,x,.82,-2.22+j*.34,dark)}
 const ssd=group('ssd');box(ssd,2.1,.07,.64,-.17,.27,.25,mat(0x253f4a));box(ssd,1.25,.04,.53,-.2,.33,.25,black);box(ssd,.72,.009,.39,-.28,.356,.25,silver);box(ssd,.15,.025,.59,.87,.28,.25,gold);
 const cooler=group('cooler');for(let i=0;i<12;i++)box(cooler,1.55,.055,1.5,-.45,.64+i*.074,-1.2,silver);box(cooler,1.7,.18,1.65,-.45,1.55,-1.2,black);cylinder(cooler,.68,.14,-.45,1.69,-1.2,dark);cylinder(cooler,.2,.16,-.45,1.74,-1.2,lime);for(let i=0;i<7;i++){let blade=box(cooler,.22,.09,.53,0,0,0,black);let a=i/7*Math.PI*2;blade.position.set(-.45+Math.sin(a)*.39,1.78,-1.2+Math.cos(a)*.39);blade.rotation.y=a+.5;}
 const pcCase=group('case');const caseMat=new THREE.MeshStandardMaterial({color:0x759087,metalness:.5,roughness:.6,transparent:true,opacity:.23,depthWrite:false});box(pcCase,6.1,.12,7.1,0,-.38,0,caseMat);for(const x of [-3,3]){box(pcCase,.06,1.6,7.1,x,.35,0,caseMat);for(const z of [-3.5,3.5])box(pcCase,.07,2.1,.07,x,.55,z,silver)}box(pcCase,6,.07,.07,0,1.6,-3.5,silver);box(pcCase,6,.07,.07,0,1.6,3.5,silver);
 const gpu=group('gpu');box(gpu,3.6,1.15,.45,-.4,.94,1,black);box(gpu,3.7,.13,.5,-.4,1.58,1,silver);for(const x of [-1.28,.5]){let fan=cylinder(gpu,.44,.075,x,0,0,dark);fan.rotation.x=Math.PI/2;fan.position.set(x,.98,1.27);let hub=cylinder(gpu,.12,.09,x,0,0,lime);hub.rotation.x=Math.PI/2;hub.position.set(x,.98,1.33)}box(gpu,.07,1.6,.65,-2.35,.92,1,silver);
 const power=group('power');box(power,1.8,1.1,1.6,4.1,.1,1.8,black);box(power,1.3,.02,1.1,4.1,.67,1.8,dark);for(let i=0;i<8;i++)box(power,.07,.025,1.05,3.6+i*.14,.69,1.8,silver);
 const wireMat=mat(0xdab881,.3);for(let i=0;i<5;i++){let curve=new THREE.CatmullRomCurve3([new THREE.Vector3(3.25,.3,1.4+i*.06),new THREE.Vector3(3.1,.8,.4),new THREE.Vector3(2.7,.8,-.5+i*.08),new THREE.Vector3(2.5,.52,-.65+i*.08)]);let wire=new THREE.Mesh(new THREE.TubeGeometry(curve,24,.025,6,false),wireMat);power.add(wire)}
 const focusRing=new THREE.Mesh(new THREE.RingGeometry(.9,1,64),new THREE.MeshBasicMaterial({color:0xb9f27b,side:THREE.DoubleSide,transparent:true,opacity:.7}));focusRing.rotation.x=-Math.PI/2;root.add(focusRing);
 const locations={board:[0,.1,0,3],cpu:[-.45,.29,-1.2,1],ram:[1.6,.35,-1.2,1.5],ssd:[-.17,.23,.25,1.1],cooler:[-.45,.5,-1.2,1.2],case:[0,-.3,0,3.5],gpu:[-.4,.35,1,1.6],power:[2.5,.5,-.8,.65]};
 let current=0,exploded=false,start=performance.now(),animating=true;const order=['board','cpu','ram','ssd','cooler','case','gpu','power'];let reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
 function setStep(i){current=i;start=performance.now();animating=!reduce;for(let n=0;n<order.length;n++){groups[order[n]].visible=n<=i;groups[order[n]].position.y=0}const [x,y,z,r]=locations[order[i]];focusRing.position.set(x,y,z);focusRing.scale.set(r,r,1);focusRing.visible=true;}
 function animate(t){requestAnimationFrame(animate);if(!host.clientWidth||document.hidden)return;let elapsed=Math.min(1,(t-start)/1300);const ease=1-Math.pow(1-elapsed,3);order.forEach((name,i)=>{let target=exploded&&i>0&&name!=='case'?i*.35+.35:0;groups[name].position.y=target+(animating&&i===current&&i>0&&name!=='case'?(1-ease)*2.5:0)});if(elapsed===1)animating=false;focusRing.material.opacity=reduce?.5:.42+Math.sin(t/700)*.16;controls.update();renderer.render(scene,camera)}
 const obs=new ResizeObserver(()=>{const w=host.clientWidth,h=host.clientHeight;if(!w||!h)return;camera.aspect=w/h;camera.updateProjectionMatrix();renderer.setSize(w,h)});obs.observe(host);setStep(0);requestAnimationFrame(animate);
 return {setStep,reset,replay(){start=performance.now();animating=!reduce},explode(v){exploded=v},zoom(factor){camera.position.sub(controls.target).multiplyScalar(factor).add(controls.target);controls.update()}};
}
