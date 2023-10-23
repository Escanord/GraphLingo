//imports
import './DependencyGraph.css'

//react
import React from 'react';
import * as go from 'gojs';
import { ReactDiagram } from 'gojs-react';

//master export
export default class GoDiagramWrapper extends React.Component {
  // console.warn(props);
  // links
  // node
  // diagramRef

  constructor(props){
    super(props);

    // this.links = props.data.links;
    // this.node = props.data.nodes;
    this.diagramRef = React.createRef();
    console.warn(this.links, this.node);
  }

  update(){
    setTimeout( () => {
      console.warn(this.diagramRef.current.getDiagram());
      this.diagramRef.current.getDiagram().zoomToFit();
      // this.diagramRef.current.getDiagram().requestUpdate();
    }, 100);
    console.warn("cleared");
  }

  /**
   * Get the diagram reference and add any desired diagram listeners.
   * Typically the same function will be used for each listener,
   * with the function using a switch statement to handle the events.
   * This is only necessary when you want to define additional app-specific diagram listeners.
   */
  componentDidMount() {
    console.warn(this.links, this.node)
    if (!this.diagramRef.current) return;
    const diagram = this.diagramRef.current.getDiagram();
    if (diagram instanceof go.Diagram) {
      diagram.addDiagramListener('ChangedSelection', this.props.onDiagramEvent);
    }
  }

  /**
   * Get the diagram reference and remove listeners that were added during mounting.
   * This is only necessary when you have defined additional app-specific diagram listeners.
   */
  componentWillUnmount() {
    if (!this.diagramRef.current) return;
    const diagram = this.diagramRef.current.getDiagram();
    if (diagram instanceof go.Diagram) {
      diagram.removeDiagramListener('ChangedSelection', this.props.onDiagramEvent);
    }
  }
  
  initDiagram () {
    console.warn("hi")
    const $ = go.GraphObject.make;
    // set your license key here before creating the diagram: go.Diagram.licenseKey = "...";
    const diagram =
      $(go.Diagram,
        {
          "ViewportBoundsChanged": function(e) {
            let allowScroll = !e.diagram.viewportBounds.containsRect(e.diagram.documentBounds);
            diagram.allowHorizontalScroll = allowScroll;
            diagram.allowVerticalScroll = allowScroll;
          },
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
  render() {
    return (
        <ReactDiagram
          ref={this.diagramRef}
          divClassName='vis-dep'
          initDiagram={this.initDiagram}
          nodeDataArray={this.props.nodeDataArray}
          linkDataArray={this.props.linkDataArray}
          modelData={this.props.modelData}
          onModelChange={this.props.onModelChange}
          skipsDiagramUpdate={this.props.skipsDiagramUpdate}
        />
    )
  }
  //return master object
  
}