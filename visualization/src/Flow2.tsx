import { useCallback } from "react";
import ReactFlow, {
  MarkerType,
  useNodesState,
  useEdgesState,
  Background,
  addEdge,
  isEdge,
  MiniMap,
  Controls,
  Edge,
  Position,
  Connection,
  Node
} from "reactflow";

import { SmartBezierEdge } from '@tisoap/react-flow-smart-edge'

import "reactflow/dist/style.css";

import CustomEdge from "./CustomEdge";
import ObligationNode from "./ObligationNode";
import ActivityNode from "./ActivityNode";
import StartNode from "./StartNode";
import EndNote from "./EndNode";

import partenNodesObject from './parentNodes.json'; 
import activityNodesObject from './activityNodes.json';
import inputNodesObject from './inputNodes.json'; 
import outputNodesObject from './outputNodes.json'; 
import obligationEdgesObject from './obligationEdges.json'; 
import inputBindingEdgesObject from './inputBindingEdges.json'; 
import outputBindingEdgesObject from './outputBindingEdges.json'; 
import activityEdgesObject from './activityEdges.json'; 


const parentNodes = partenNodesObject;
const activityNodes = activityNodesObject;
const inputNodes = inputNodesObject;
const outputNodes = outputNodesObject;
const obligationEdges = obligationEdgesObject;
const inputBindingEdges = inputBindingEdgesObject;
const outputBindingEdges = outputBindingEdgesObject;
const activityEdges = activityEdgesObject;

const initialNodes: Node[] = [];
parentNodes.forEach( (node) => {
    initialNodes.push({id: node.id, data: {}, position: {x: node.pos_x, y: node.pos_y}, type:'group', style: {width: node.width, height: node.height, background:'rgba(255,255,255,0.05)'}});
});
activityNodes.forEach( (node) => {
    initialNodes.push({id: node.id, data: {activityID: node.id, activityName: node.activity, objectTypes: node.objectTypes}, position: {x: node.pos_x, y: node.pos_y}, type:node.type, parentNode: node.parent_id,
    extent: "parent",
    draggable: true});
});
inputNodes.forEach( (node) => {
    initialNodes.push({id: node.id, data: {obligationID: node.index, objectType:node.objectType, objectMin:node.object_min, objectMax:node.object_max, radius:node.radius}, position: {x: node.pos_x, y: node.pos_y}, type:'obligation', parentNode: node.parent_id,
    extent: "parent",
    draggable: true});
    console.log(node.object_max);
});
outputNodes.forEach( (node) => {
    initialNodes.push({id: node.id, data: {obligationID: node.index, objectType:node.objectType, objectMin:node.object_min, objectMax:node.object_max, radius:node.radius}, position: {x: node.pos_x, y: node.pos_y}, type:'obligation', parentNode: node.parent_id,
    extent: "parent",
    draggable: true});
});

const initialEdges: Edge[] = [];
obligationEdges.forEach( (edge) => {
    initialEdges.push({id: edge.id, source: edge.start_id, target: edge.end_id, sourceHandle: "binding_out",
    targetHandle: "binding_in", type: "default", style: { strokeWidth: 2, stroke: "#FFFFFF" }});
});
inputBindingEdges.forEach( (edge) => {
    initialEdges.push({id: edge.id, source: edge.start_id, target: edge.end_id, sourceHandle: "dependency_out",
    targetHandle: "dependency_in", type: "default", style: { strokeWidth: 2, stroke: "#FFFFFF" }});
});
outputBindingEdges.forEach( (edge) => {
    initialEdges.push({id: edge.id, source: edge.start_id, target: edge.end_id, sourceHandle: "dependency_out",
    targetHandle: "dependency_in", type: "default", style: { strokeWidth: 2, stroke: "#FFFFFF" }});
});
activityEdges.forEach( (edge) => {
    initialEdges.push({id: edge.id, source: edge.start_id, target: edge.end_id, sourceHandle: "dependency_out",
    targetHandle: "dependency_in", type: "custom", style: { strokeWidth: 2, stroke: "#FFFFFF" },
    data:{start_activity: edge.start_activity, end_activity: edge.end_activity}});
});

const edgeTypes = {
    custom: CustomEdge,
    smart: SmartBezierEdge
  };
  
const nodeTypes = {
  obligation: ObligationNode,
  activity: ActivityNode,
  start: StartNode,
  end: EndNote
};

//const defaultViewport = { x: 0, y: 0, zoom: 0.1 };
  
const BasicFlow = () => {
  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const onConnect = useCallback(
    (params: Edge | Connection) => setEdges((els) => addEdge(params, els)),
    [setEdges]
  );
  
  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onConnect={onConnect}
      edgeTypes={edgeTypes}
      nodeTypes={nodeTypes}
      //defaultViewport = {defaultViewport}
      fitView
      minZoom = {0.1}
      snapToGrid = {true}
      snapGrid={[10,10]}
    >
      <Background
        id="1"
        gap={20}
        color="#f1f1f1"
      />
    </ReactFlow>
  );
};
  
  export default BasicFlow;
  