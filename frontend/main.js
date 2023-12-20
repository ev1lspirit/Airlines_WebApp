import './style.css'
import javascriptLogo from './javascript.svg'
import viteLogo from '/vite.svg'
import { setupCounter } from './counter.js'
import * as THREE from '../three'
import { OrbitControls } from '../three/examples/jsm/controls/OrbitControls'
import vertexShader from './shaders/vertex.glsl'
import fragmentShader from './shaders/fragment.glsl'
import atmosdphereFragmentShader from './shaders/atmosphereFragment.glsl'
import atmosdphereVertexShader from './shaders/atmosphereVertex.glsl'
import {PlaneModel} from './models.js';
import bootstrap from "bootstrap/dist/css/bootstrap.css"



var scene, camera, renderer;
var controls;
var pointLight;
var canvas;

function init()
{
  canvas = document.getElementById("bg");
  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(30, window.innerWidth / window.innerHeight, 0.1, 1500);
  renderer = new THREE.WebGLRenderer(
  {canvas: canvas,
  antialias: true});

  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(window.innerWidth, window.innerHeight);
  document.body.appendChild(renderer.domElement);
  camera.position.set(0, 0, 20);

  pointLight = new THREE.PointLight(0xffffff, 1, 100);
  pointLight.position.set(-10, 50, -20);
  scene.add(pointLight);

  scene.background = new THREE.Color(0x000000) // 0x0A0014

  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableZoom = false;
  scene.fog = new THREE.Fog(0x535ef3, 400, 2000);
}
init();
// addAxes(10);


function addAxes(length)
{
  let axes = new THREE.AxesHelper(length);
  scene.add(axes);
}

function drawSphere(sphereMaterial, radius, w_segments, h_segments)
{
  var sphere = new THREE.SphereGeometry(radius, w_segments, h_segments);
  var sphereMesh = new THREE.Mesh(sphere, sphereMaterial);
  sphereMesh.metadata = {};
  sphereMesh.metadata.x_angle = 0;
  sphereMesh.metadata.y_angle = 0;
  return sphereMesh;
}

function Orbit(radius, phi_angle, o_angle, mesh)
{
  this.radius = radius;
  this.phi_angle = phi_angle;
  this.o_angle = o_angle;
  this.speed = 1;
  this.mesh = mesh;
  this.multiplier = -1;


  this.performSinMovement = function()
  {
    this.updateMeshCoordinates(this.mesh);
    this.phi_angle += (Math.PI / 30) * this.speed;
    this.o_angle += Math.PI / 30 * this.speed;


    console.log('\n');
    console.log(this.phi_angle, this.o_angle);
    console.log('\n');

    //this.mesh.rotation.x += this.phi_angle / 50 ;
    //this.mesh.rotation.z -= Math.PI / 50;


    if (this.phi_angle > Math.PI)
    {
      this.phi_angle = -Math.PI + 2 * Math.PI / 100 * this.speed;
    }
    if (this.o_angle > 2 * Math.PI )
    {
      this.multiplier *= -1;
      this.o_angle = 2 * Math.PI / 100 * this.speed;
    }
    this.mesh.rotation.y = (this.o_angle + (Math.PI / 30) * this.speed) - this.o_angle;
//    this.mesh.rotation.x = this.o_angle / 20000 * this.multiplier;
  }

  this.updateMeshCoordinates = function ()
  {
    let CoordinateX = this.radius * Math.cos(this.phi_angle) * Math.sin(this.o_angle);
    let CoordinateY = this.radius * Math.sin(this.phi_angle) * Math.sin(this.o_angle);
    let CoordinateZ = this.radius * Math.cos(this.o_angle);
    this.mesh.position.x = CoordinateX;
    this.mesh.position.y = CoordinateZ;
    this.mesh.position.z = CoordinateY;
    return new THREE.Vector3(CoordinateX, CoordinateZ, CoordinateY);
  }

  this.setSpeed = function(speed)
  {
    this.speed = speed;
  }

  this.moveByCircle = function () {
    this.updateMeshCoordinates(this.mesh);
  //  this.o_angle -= Math.PI / 30 * this.speed;
  
    this.mesh.rotation.x += 0.01;

    console.log('\n');
    console.log(this.mesh.rotation.x);
    console.log('\n');

    if (this.phi_angle > Math.PI) {
      this.phi_angle = -Math.PI + 2 * Math.PI / 30 * this.speed;
    }
    if (this.o_angle < 0) {
      this.o_angle = 2 * Math.PI - 2 * Math.PI / 30 * this.speed;
    }
  //  this.mesh.rotation.y -= (this.o_angle + (Math.PI / 30) * this.speed) - this.o_angle;
  }
}

let planet;
function initPlanet() {
  const planetMaterial = new THREE.ShaderMaterial(
    {
      vertexShader: vertexShader,
      fragmentShader: fragmentShader,
      uniforms: {
        globeTexture: {
          value: new THREE.TextureLoader().load('./earth_texture.jpg')
        }
      }
    });
  planet = drawSphere(planetMaterial, 2.8, 32, 32);
  planet.position.set(0, 0, 0);
}

function initAtmosphere()
  {
    const atmosphereMaterial = new THREE.ShaderMaterial(
      {
        vertexShader: atmosdphereVertexShader,
        fragmentShader: atmosdphereFragmentShader,
        blending: THREE.AdditiveBlending,
        side: THREE.BackSide
      });
    let atmosphere = drawSphere(atmosphereMaterial, 3.5, 32, 32);
    scene.add(atmosphere);
  }


let ellipseSphere;
function initParticle()
{
  let sphereMaterial = new THREE.MeshBasicMaterial({ color: 0xFFFFFF });
  ellipseSphere = drawSphere(sphereMaterial, 0.03, 32, 32);
  scene.add(ellipseSphere);
}

initPlanet();
initAtmosphere();
initParticle();

let sin_orbits = [];
let sputnik_o_angle = Math.PI / 2;
let sputnik_phi_angle = -Math.PI;
let new_sputnik;

let plane = new PlaneModel(3).initPlane();
plane.scale.set(0.005, 0.005, 0.005);

for (let i = 0; i < 2; ++i)
{
  let clone = plane.clone();
  clone.rotation.x = Math.PI / 3;
  clone.rotation.z = Math.PI;
  clone.rotation.y = 0;
  scene.add(clone);
  new_sputnik = new Orbit(3.1 - Math.random() * 0.1 , sputnik_phi_angle, sputnik_o_angle, clone);
  new_sputnik.setSpeed(0.01);
  sin_orbits.push(new_sputnik); 
  sputnik_o_angle -= 1 + Math.random() * i * Math.PI / 4;
  sputnik_phi_angle -= 1 + Math.random() * i;
}


// event listeners
window.addEventListener('mousemove', onMouseMove, false);

const sphereGroup = new THREE.Group();
sphereGroup.add(planet);
scene.add(sphereGroup);


const mouse = {
  x: undefined,
  y: undefined
}

function onMouseMove(event)
{
  mouse.x = (event.clientX / innerWidth) * 2 - 1;
  mouse.y = (event.clientY / innerWidth) * 2 - 1;
}

function animate()
{
  requestAnimationFrame(animate);
  planet.rotation.y += 0.005;
  sphereGroup.rotation.y = mouse.x * 0.3;

  // controls.update();
  renderer.render(scene, camera);
}


// setupCounter(document.querySelector('#counter'))
animate();
