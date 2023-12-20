import * as THREE from 'three';


const extrudeSettings = {
    depth: 0.1,
    bevelEnabled: true,
    bevelSegments: 2,
    steps: 2, 
    bevelSize: 0.1,
    bevelThickness: 0.1
}


export function PlaneModel(fuselageRadius)
{
    this.fuselageRadius = fuselageRadius;
    this.body = function () {
        let bodyMaterial = new THREE.MeshLambertMaterial({ color: 0xffffff });

        function drawNose()
        {
            let noseGeometry = new THREE.SphereGeometry(fuselageRadius, 32, 16, 0, Math.PI);
            return new THREE.Mesh(noseGeometry, bodyMaterial);
        }

        let bodyObject = new THREE.Object3D();
        let bodyGeometry = new THREE.CylinderGeometry(fuselageRadius, fuselageRadius, 30, 32, 32);
        let bodyMesh = new THREE.Mesh(bodyGeometry, bodyMaterial);
        let noseMesh = drawNose();
        noseMesh.position.set(0, -15, 0);
        noseMesh.scale.setZ(2.2);
        noseMesh.rotation.x = Math.PI / 2;
        bodyObject.add(bodyMesh, noseMesh);
        return bodyObject;
    }

    this.wing = function () {
        let wingShape = new THREE.Shape();
        wingShape.moveTo(0, 0);
        wingShape.lineTo(7, 5);
        wingShape.quadraticCurveTo(8.9, 6, 9, 5);
        wingShape.quadraticCurveTo(7, 4, 3, 0);
        wingShape.lineTo(0, 0);

        let basicMaterial = new THREE.MeshBasicMaterial({color: "color"});
        const shapeGeometry = new THREE.ExtrudeGeometry(
            wingShape,
            extrudeSettings
        );

        return new THREE.Mesh(shapeGeometry, basicMaterial);
    }

    this.tail = function() {
        let tailShape = new THREE.Shape();
        tailShape.moveTo(0, 0);
        tailShape.lineTo(1.7, 2);
        tailShape.quadraticCurveTo(1.85, 2.1, 2, 2);
        tailShape.lineTo(1.5, 0);

       // let geomShape = new THREE.ShapeBufferGeometry(tailShape);
        let basicMaterial = new THREE.MeshBasicMaterial({color: "blue"});
        const shapeGeometry = new THREE.ExtrudeGeometry(
            tailShape,
            extrudeSettings
        );
        return new THREE.Mesh(shapeGeometry, basicMaterial);
       // let shapeMesh = new THREE.Mesh(geomShape, basicMaterial);
    }


    this.fuselageEnd = function () {
        let fuselageEnd3D = new THREE.Group();
        let basicMaterial = new THREE.MeshLambertMaterial({color: "color"});
        let torusEndGeometry = new THREE.TorusGeometry(this.fuselageRadius, 3, 64, 100, Math.PI / 12);
        let torusEndMesh = new THREE.Mesh(torusEndGeometry, basicMaterial);
        let cylinderEndGeometry = new THREE.CylinderGeometry(this.fuselageRadius, 0.5, 10, 64, 64);
        let cylinderEndMesh = new THREE.Mesh(cylinderEndGeometry, basicMaterial);

        torusEndMesh.rotation.x = - Math.PI / 2;
        torusEndMesh.rotation.y = Math.PI / 2;
        torusEndMesh.rotation.z = -Math.PI / 13;

        cylinderEndMesh.rotation.x = - Math.PI / 2 - Math.PI / 13;
    
        torusEndMesh.position.set(0, 3, 15);
        cylinderEndMesh.position.set(0, 1.29, 20.56);

        fuselageEnd3D.add(torusEndMesh);
        fuselageEnd3D.add(cylinderEndMesh);
        return fuselageEnd3D;
    }


    this.initPlane = function () {
        let plane = new THREE.Object3D();
        let planeBody3D = this.body();
        planeBody3D.rotation.x = Math.PI / 2;

        let fuselageEnd3D = this.fuselageEnd();
        let wing1 = this.wing();
        wing1.scale.set(3,3,3);
        wing1.rotation.x = -Math.PI / 2;
        wing1.rotation.z = -Math.PI / 2;
        wing1.position.set(0, 0, -15);
        let wing2 = wing1.clone();

        wing2.rotation.y = Math.PI;
        let tail = this.tail();

        tail.rotation.y = -Math.PI / 2;
        tail.scale.set(4, 4, 2);
        tail.position.set(0.07, 2.05, 18);

        let tail2 = this.tail();
      //  let tail3 = tail.clone();
        tail2.rotation.x = -Math.PI / 2;
        tail2.rotation.z = -Math.PI / 2;
        tail2.rotation.y = Math.PI / 32;
        tail2.position.set(0.07, 2.05, 17);
        tail2.scale.set(4, 4, 2);

        let tail3 = tail2.clone();
        tail3.rotation.x = Math.PI / 2;
        tail3.rotation.z = Math.PI / 2;
        tail3.rotation.x = Math.PI / 2;
        tail2.rotation.y = Math.PI / 32;
        tail3.position.set(0.07, 2.05, 17);

        plane.add(planeBody3D, fuselageEnd3D);
        plane.add(wing1, wing2);
        plane.add(tail, tail2, tail3);
        return plane;
    }
}