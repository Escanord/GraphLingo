//imports
import './DependencyGraph.css'

//react
import React from 'react';
import * as go from 'gojs';
import { ReactDiagram } from 'gojs-react';

//master export
export default function DependencyGraph(props) {
  // console.warn(props);
  const links = props.data.links;
  const nodes = props.data.nodes;

  let initDiagram = () =>{
    const $ = go.GraphObject.make;
  // set your license key here before creating the diagram: go.Diagram.licenseKey = "...";
  const diagram =
    $(go.Diagram,
      {
        'undoManager.isEnabled': true,  // must be set to allow for model change listening
        // 'undoManager.maxHistoryLength': 0,  // uncomment disable undo/redo functionality
        'clickCreatingTool.archetypeNodeData': { text: 'new node', color: 'lightblue' },
        model: new go.GraphLinksModel(
          {
            linkKeyProperty: 'key'  // IMPORTANT! must be defined for merges and data sync when using GraphLinksModel
          }),
        layout: $(go.LayeredDigraphLayout, // specify a Diagram.layout that arranges trees
          { 
              direction: 90, 
              layerSpacing: 35,
              aggressiveOption: go.LayeredDigraphLayout.AggressiveMore
          })
      });

    // the template for displaying the graph in case formatting
    diagram.nodeTemplate =
    $(go.Node, "Horizontal", { background: "#0a304e" },
        $(go.TextBlock, "none", { margin: 12, stroke: "white", font: "bold 14px Titillium Web, sans-serif" },new go.Binding("text", "name"))
    );
    return diagram;
  }

  function handleModelChange(changes) {
    // alert('GoJS model changed!');
  }


  //return master object
  return (
    <>
      <ReactDiagram
      initDiagram = {initDiagram}
      divClassName = 'vis-dep'
      nodeDataArray={nodes}
      linkDataArray={links}
      onModelChange={handleModelChange}/>
    </>
      )
}