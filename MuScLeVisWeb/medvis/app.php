<?php
// Initialize the session
session_start();
 
// Check if the user is logged in, if not then redirect him to login page
if(!isset($_SESSION["loggedin"]) || $_SESSION["loggedin"] !== true){
    header("location: login.php");
    exit;
}
?>

<!DOCTYPE html>
<html>
<link href="app.css" rel="stylesheet" type="text/css" />
<link href="https://fonts.googleapis.com/css?family=Montserrat&display=swap" rel="stylesheet">
<style type="text/css">
	body{
		margin-left: 0px;
		margin-top: 0px;
		margin-right: 0px;
		margin-bottom: 0px;
	}
</style>
<script type="text/javascript" src="https://unpkg.com/@babel/polyfill@7.0.0/dist/polyfill.js"></script>
<script type="text/javascript" src="https://unpkg.com/vtk.js"></script>
<script type="text/javascript">
	
function dataLoader(actors, mappers, objReaders, selectedItem, surfaces, renderer, renderWindow){
for (let i = 0; i < 2; i++) { 
actors.push(vtk.Rendering.Core.vtkActor.newInstance());
mappers.push(vtk.Rendering.Core.vtkMapper.newInstance());
objReaders.push(vtk.IO.Misc.vtkOBJReader.newInstance());
objReaders[i].setUrl("./data/"+selectedItem.value+"/surfaces/" + surfaces[i]).then(() => {
var polyData = objReaders[i].getOutputData(0);
mappers[i].setInputData(polyData);
actors[i].setMapper(mappers[i]);
renderer.addActor(actors[i]);
renderer.setBackground(0.2,0.2,0.2);
renderer.resetCamera();
renderWindow.render();
console.log("Finished " + i);
});
	} // end for
console.log("Done with looping");
}
	
function refreshScene() {
	alert("sdfdsf");
}
	
function loadSurfaceData() {
//var fullScreenRenderer = vtk.Rendering.Misc.vtkGenericRenderWindowWithControlBar.newInstance({
//  controlSize: 0,
//  background: [0, 0, 0],
//});
	
const fullScreenRenderer = vtk.Rendering.Misc.vtkRenderWindowWithControlBar.newInstance({
  controlSize: 0,
});

//var actor       = vtk.Rendering.Core.vtkActor.newInstance();
//var mapper      = vtk.Rendering.Core.vtkMapper.newInstance();
//const objReaderL = vtk.IO.Misc.vtkOBJReader.newInstance();
//const objReaderR = vtk.IO.Misc.vtkOBJReader.newInstance();
const glwindow = vtk.Rendering.OpenGL.vtkRenderWindow.newInstance();	

var selectCtrl = document.getElementById("slctPatient");
var selectedItem = selectCtrl.options[selectCtrl.selectedIndex];

const surfaces = ["rh.pial.obj", "lh.pial.obj"];
const renderer = fullScreenRenderer.getRenderer();
const renderWindow = fullScreenRenderer.getRenderWindow();
const container = document.getElementById('tdcontent');
fullScreenRenderer.setContainer(container);
	
var actors = new Array();
var mappers = new Array();
var objReaders = new Array();

dataLoader(actors, mappers, objReaders, selectedItem, surfaces, renderer, renderWindow);
//for (let i = 0; i < 2; i++) { 
//console.log("Start" + i)
//actors.push(vtk.Rendering.Core.vtkActor.newInstance());
//mappers.push(vtk.Rendering.Core.vtkMapper.newInstance());
//objReaders.push(vtk.IO.Misc.vtkOBJReader.newInstance());
////var objR = objReader[i];
//objReaders[i].setUrl("./data/"+selectedItem.value+"/surfaces/" + surfaces[i]).then(() => {
//var polyData = objReaders[i].getOutputData(0);
//console.log("iteration"+i)	
//mappers[i].setInputData(polyData);
//actors[i].setMapper(mappers[i]);
//renderer.addActor(actors[i]);
//renderer.setBackground(0.2,0.2,0.2);
//renderer.resetCamera();
//renderWindow.render();
//});
//console.log("End" + i);
//	}

};
	
</script>
<body>

<div id="header"><img style="padding-left: 20px; padding-top: 6px" src="./webLogo.png" width="180" alt=""/><a href="logout.php" id="logoutBtn">Log Out</a></div>
<div id="mainControls">
<div class="select">
  <select name="slct" id="slctPatient">
    <option selected disabled>Select a patient</option>
<!--	<option value="1">01016SACH_DATA</option>
    <option value="2">01038PAGU_DATA</option>
    <option value="3">01039VITE_DATA</option>-->
    <option value="01040VANE_DATA">01040VANE_DATA</option>
<!--	<option value="3">01042GULE_DATA</option>-->
	<option value="07001MOEL_DATA">07001MOEL_DATA</option>
<!--	<option value="3">07003SATH_DATA</option>-->
	<option value="07010NABO_DATA">07010NABO_DATA</option>
	<option value="07040DORE_DATA">07040DORE_DATA</option>
<!--	<option value="3">07043SEME_DATA</option>
	<option value="3">08002CHJE_DATA</option>-->
	<option value="08027SYBR_DATA">08027SYBR_DATA</option>
<!--	<option value="3">08029IVDI_DATA</option>
	<option value="3">08031SEVE_DATA</option>
	<option value="3">08037ROGU_DATA</option>-->
  </select>
</div><br>
<div class="select">
  <select name="slct" id="slctVisualization">
    <option selected disabled>Select a visualization</option>
    <option value="1">Lesions View - Basic</option>
    <option value="2">Lesions View - Surface Map</option>
    <option value="3">Lesions View - Temporal Map</option>
  </select>
</div><br>
  <button name="buttonRenderSurfaceData" id="buttonRenderSurfaceData" onClick="loadSurfaceData()">Render Surface Data</button><br>
  <button name="buttonRenderVolumeData" id="buttonRenderVolumeData">Render Volume Data</button><br>
  <label for="textareaLoadedSurfaceData" style="margin-left: 5px;">Loaded Surface Data</label><br>
  <textarea name="textareaLoadedSurfaceData" id="textareaLoadedSurfaceData"></textarea><br>
  <button name="buttonUnselectAllSurfaceData" id="buttonUnselectAllSurfaceData">Unselect All</button><br>
  <label for="textareaLoadedStructural" style="margin-left: 5px;">Loaded Structural Data</label><br>
  <textarea name="textareaLoadedStructural" id="textareaLoadedStructural"></textarea><br>
  <label for="selectFilterLesions" style="margin-left: 5px;">Filter Lesions:</label><br>
  <div class="select">
  <select name="slct" id="slctFilter">
    <option selected disabled>Choose a filter param</option>
    <option value="1">Voxel Count</option>
    <option value="2">Elongation</option>
    <option value="3">Perimeter</option>
	<option value="4">Spherical Radius</option>
	<option value="5">Spherical Parameter</option>
	<option value="6">Flatness</option>
	<option value="7">Roundness</option>
  </select>
</div>
</div>
	
<div id="MPRs">
<div id="MPRA">MPRA</div>
<div id="MPRB">MPRB</div>
<div id="MPRC">MPRC</div>
</div>
<div id="protocols"></div>
<!--<div id="VR"></div>-->
	
<table id="page">
    <tr>
        <td id="tdcontent">
        </td>
    </tr>
</table>
	
	
</body>
</html>