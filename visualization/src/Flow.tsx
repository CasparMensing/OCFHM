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


const initialNodes: Node[] = [
  { 
  id: "parent_Create_Purchase_Requisition",
  data: {},
  position: {x: -2400, y: 0},
  type:"group",
  style: {width: 280, height: 200}
  },{ 
  id: "Create_Purchase_Requisition",
  data: {activityID: "Create_Purchase_Requisition", activityName: "Create Purchase Requisition"},
  position: {x: 65.0, y: 50.0},
  type:"activity",
  parentNode: "parent_Create_Purchase_Requisition",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Create_Purchase_Requisition_in_0_0",
  data: {obligationID: "0", objectType: "MATERIAL"},
  position: {x: 25.0, y: 72.0},
  type:"obligation",
  parentNode: "parent_Create_Purchase_Requisition",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Create_Purchase_Requisition_in_0_1",
  data: {obligationID: "0", objectType: "PURCHREQ"},
  position: {x: 25.0, y: 112.0},
  type:"obligation",
  parentNode: "parent_Create_Purchase_Requisition",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Create_Purchase_Requisition_out_0_0",
  data: {obligationID: "0", objectType: "PURCHREQ"},
  position: {x: 235.0, y: 72.0},
  type:"obligation",
  parentNode: "parent_Create_Purchase_Requisition",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Create_Purchase_Requisition_out_0_1",
  data: {obligationID: "0", objectType: "MATERIAL"},
  position: {x: 235.0, y: 112.0},
  type:"obligation",
  parentNode: "parent_Create_Purchase_Requisition",
  extent: "parent",
  draggable: true
  },{ 
  id: "parent_Issue_Goods_Receipt",
  data: {},
  position: {x: -1200, y: 0},
  type:"group",
  style: {width: 280, height: 280}
  },{ 
  id: "Issue_Goods_Receipt",
  data: {activityID: "Issue_Goods_Receipt", activityName: "Issue Goods Receipt"},
  position: {x: 65.0, y: 90.0},
  type:"activity",
  parentNode: "parent_Issue_Goods_Receipt",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Issue_Goods_Receipt_in_0_0",
  data: {obligationID: "0", objectType: "PURCHORD"},
  position: {x: 25.0, y: 92.0},
  type:"obligation",
  parentNode: "parent_Issue_Goods_Receipt",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Issue_Goods_Receipt_in_0_1",
  data: {obligationID: "0", objectType: "GDSRCPT"},
  position: {x: 25.0, y: 132.0},
  type:"obligation",
  parentNode: "parent_Issue_Goods_Receipt",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Issue_Goods_Receipt_in_0_2",
  data: {obligationID: "0", objectType: "MATERIAL"},
  position: {x: 25.0, y: 172.0},
  type:"obligation",
  parentNode: "parent_Issue_Goods_Receipt",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Issue_Goods_Receipt_out_0_0",
  data: {obligationID: "0", objectType: "GDSRCPT"},
  position: {x: 235.0, y: 72.0},
  type:"obligation",
  parentNode: "parent_Issue_Goods_Receipt",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Issue_Goods_Receipt_out_0_1",
  data: {obligationID: "0", objectType: "PURCHORD"},
  position: {x: 235.0, y: 112.0},
  type:"obligation",
  parentNode: "parent_Issue_Goods_Receipt",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Issue_Goods_Receipt_out_0_2",
  data: {obligationID: "1", objectType: "MATERIAL"},
  position: {x: 235.0, y: 152.0},
  type:"obligation",
  parentNode: "parent_Issue_Goods_Receipt",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Issue_Goods_Receipt_out_0_3",
  data: {obligationID: "0", objectType: "MATERIAL"},
  position: {x: 235.0, y: 192.0},
  type:"obligation",
  parentNode: "parent_Issue_Goods_Receipt",
  extent: "parent",
  draggable: true
  },{ 
  id: "parent_Receive_Invoice",
  data: {},
  position: {x: -800, y: 0},
  type:"group",
  style: {width: 280, height: 200}
  },{ 
  id: "Receive_Invoice",
  data: {activityID: "Receive_Invoice", activityName: "Receive Invoice"},
  position: {x: 65.0, y: 50.0},
  type:"activity",
  parentNode: "parent_Receive_Invoice",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Receive_Invoice_in_0_0",
  data: {obligationID: "0", objectType: "PURCHORD"},
  position: {x: 25.0, y: 72.0},
  type:"obligation",
  parentNode: "parent_Receive_Invoice",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Receive_Invoice_in_0_1",
  data: {obligationID: "0", objectType: "INVOICE"},
  position: {x: 25.0, y: 112.0},
  type:"obligation",
  parentNode: "parent_Receive_Invoice",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Receive_Invoice_out_0_0",
  data: {obligationID: "0", objectType: "PURCHORD"},
  position: {x: 235.0, y: 72.0},
  type:"obligation",
  parentNode: "parent_Receive_Invoice",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Receive_Invoice_out_0_1",
  data: {obligationID: "0", objectType: "INVOICE"},
  position: {x: 235.0, y: 112.0},
  type:"obligation",
  parentNode: "parent_Receive_Invoice",
  extent: "parent",
  draggable: true
  },{ 
  id: "parent_Receive_Goods",
  data: {},
  position: {x: -1600, y: 0},
  type:"group",
  style: {width: 280, height: 240}
  },{ 
  id: "Receive_Goods",
  data: {activityID: "Receive_Goods", activityName: "Receive Goods"},
  position: {x: 65.0, y: 70.0},
  type:"activity",
  parentNode: "parent_Receive_Goods",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Receive_Goods_in_0_0",
  data: {obligationID: "0", objectType: "MATERIAL"},
  position: {x: 25.0, y: 72.0},
  type:"obligation",
  parentNode: "parent_Receive_Goods",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Receive_Goods_in_0_1",
  data: {obligationID: "0", objectType: "PURCHORD"},
  position: {x: 25.0, y: 112.0},
  type:"obligation",
  parentNode: "parent_Receive_Goods",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Receive_Goods_in_0_2",
  data: {obligationID: "0", objectType: "GDSRCPT"},
  position: {x: 25.0, y: 152.0},
  type:"obligation",
  parentNode: "parent_Receive_Goods",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Receive_Goods_out_0_0",
  data: {obligationID: "0", objectType: "PURCHORD"},
  position: {x: 235.0, y: 72.0},
  type:"obligation",
  parentNode: "parent_Receive_Goods",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Receive_Goods_out_0_1",
  data: {obligationID: "0", objectType: "MATERIAL"},
  position: {x: 235.0, y: 112.0},
  type:"obligation",
  parentNode: "parent_Receive_Goods",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Receive_Goods_out_0_2",
  data: {obligationID: "0", objectType: "GDSRCPT"},
  position: {x: 235.0, y: 152.0},
  type:"obligation",
  parentNode: "parent_Receive_Goods",
  extent: "parent",
  draggable: true
  },{ 
  id: "parent_Plan_Goods_Issue",
  data: {},
  position: {x: -800, y: 300},
  type:"group",
  style: {width: 280, height: 160}
  },{ 
  id: "Plan_Goods_Issue",
  data: {activityID: "Plan_Goods_Issue", activityName: "Plan Goods Issue"},
  position: {x: 65.0, y: 30.0},
  type:"activity",
  parentNode: "parent_Plan_Goods_Issue",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Plan_Goods_Issue_in_0_0",
  data: {obligationID: "0", objectType: "MATERIAL"},
  position: {x: 25.0, y: 72.0},
  type:"obligation",
  parentNode: "parent_Plan_Goods_Issue",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Plan_Goods_Issue_out_0_0",
  data: {obligationID: "0", objectType: "MATERIAL"},
  position: {x: 235.0, y: 72.0},
  type:"obligation",
  parentNode: "parent_Plan_Goods_Issue",
  extent: "parent",
  draggable: true
  },{ 
  id: "parent_Verify_Material",
  data: {},
  position: {x: -800, y: 600},
  type:"group",
  style: {width: 280, height: 160}
  },{ 
  id: "Verify_Material",
  data: {activityID: "Verify_Material", activityName: "Verify Material"},
  position: {x: 65.0, y: 30.0},
  type:"activity",
  parentNode: "parent_Verify_Material",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Verify_Material_in_0_0",
  data: {obligationID: "0", objectType: "MATERIAL"},
  position: {x: 25.0, y: 72.0},
  type:"obligation",
  parentNode: "parent_Verify_Material",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Verify_Material_out_0_0",
  data: {obligationID: "0", objectType: "MATERIAL"},
  position: {x: 235.0, y: 72.0},
  type:"obligation",
  parentNode: "parent_Verify_Material",
  extent: "parent",
  draggable: true
  },{ 
  id: "parent_Goods_Issue",
  data: {},
  position: {x: -400, y: 0},
  type:"group",
  style: {width: 280, height: 200}
  },{ 
  id: "Goods_Issue",
  data: {activityID: "Goods_Issue", activityName: "Goods Issue"},
  position: {x: 65.0, y: 50.0},
  type:"activity",
  parentNode: "parent_Goods_Issue",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Goods_Issue_in_0_0",
  data: {obligationID: "1", objectType: "MATERIAL"},
  position: {x: 25.0, y: 72.0},
  type:"obligation",
  parentNode: "parent_Goods_Issue",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Goods_Issue_in_0_1",
  data: {obligationID: "0", objectType: "MATERIAL"},
  position: {x: 25.0, y: 112.0},
  type:"obligation",
  parentNode: "parent_Goods_Issue",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Goods_Issue_out_0_0",
  data: {obligationID: "0", objectType: "MATERIAL"},
  position: {x: 235.0, y: 92.0},
  type:"obligation",
  parentNode: "parent_Goods_Issue",
  extent: "parent",
  draggable: true
  },{ 
  id: "parent_Create_Purchase_Order",
  data: {},
  position: {x: -2000, y: 0},
  type:"group",
  style: {width: 280, height: 240}
  },{ 
  id: "Create_Purchase_Order",
  data: {activityID: "Create_Purchase_Order", activityName: "Create Purchase Order"},
  position: {x: 65.0, y: 70.0},
  type:"activity",
  parentNode: "parent_Create_Purchase_Order",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Create_Purchase_Order_in_0_0",
  data: {obligationID: "0", objectType: "PURCHREQ"},
  position: {x: 25.0, y: 72.0},
  type:"obligation",
  parentNode: "parent_Create_Purchase_Order",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Create_Purchase_Order_in_0_1",
  data: {obligationID: "0", objectType: "MATERIAL"},
  position: {x: 25.0, y: 112.0},
  type:"obligation",
  parentNode: "parent_Create_Purchase_Order",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Create_Purchase_Order_in_0_2",
  data: {obligationID: "0", objectType: "PURCHORD"},
  position: {x: 25.0, y: 152.0},
  type:"obligation",
  parentNode: "parent_Create_Purchase_Order",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Create_Purchase_Order_out_0_0",
  data: {obligationID: "0", objectType: "PURCHORD"},
  position: {x: 235.0, y: 72.0},
  type:"obligation",
  parentNode: "parent_Create_Purchase_Order",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Create_Purchase_Order_out_0_1",
  data: {obligationID: "0", objectType: "MATERIAL"},
  position: {x: 235.0, y: 112.0},
  type:"obligation",
  parentNode: "parent_Create_Purchase_Order",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Create_Purchase_Order_out_0_2",
  data: {obligationID: "0", objectType: "PURCHREQ"},
  position: {x: 235.0, y: 152.0},
  type:"obligation",
  parentNode: "parent_Create_Purchase_Order",
  extent: "parent",
  draggable: true
  },{ 
  id: "parent_Clear_Invoice",
  data: {},
  position: {x: -400, y: 300},
  type:"group",
  style: {width: 280, height: 240}
  },{ 
  id: "Clear_Invoice",
  data: {activityID: "Clear_Invoice", activityName: "Clear Invoice"},
  position: {x: 65.0, y: 70.0},
  type:"activity",
  parentNode: "parent_Clear_Invoice",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Clear_Invoice_in_0_0",
  data: {obligationID: "0", objectType: "INVOICE"},
  position: {x: 25.0, y: 72.0},
  type:"obligation",
  parentNode: "parent_Clear_Invoice",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Clear_Invoice_in_0_1",
  data: {obligationID: "0", objectType: "PURCHORD"},
  position: {x: 25.0, y: 112.0},
  type:"obligation",
  parentNode: "parent_Clear_Invoice",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Clear_Invoice_in_0_2",
  data: {obligationID: "0", objectType: "GDSRCPT"},
  position: {x: 25.0, y: 152.0},
  type:"obligation",
  parentNode: "parent_Clear_Invoice",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Clear_Invoice_out_0_0",
  data: {obligationID: "0", objectType: "GDSRCPT"},
  position: {x: 235.0, y: 72.0},
  type:"obligation",
  parentNode: "parent_Clear_Invoice",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Clear_Invoice_out_0_1",
  data: {obligationID: "0", objectType: "INVOICE"},
  position: {x: 235.0, y: 112.0},
  type:"obligation",
  parentNode: "parent_Clear_Invoice",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_Clear_Invoice_out_0_2",
  data: {obligationID: "0", objectType: "PURCHORD"},
  position: {x: 235.0, y: 152.0},
  type:"obligation",
  parentNode: "parent_Clear_Invoice",
  extent: "parent",
  draggable: true
  },{ 
  id: "parent_GDSRCPT_START",
  data: {},
  position: {x: -2000, y: 300},
  type:"group",
  style: {width: 240, height: 160}
  },{ 
  id: "GDSRCPT_START",
  data: {activityID: "GDSRCPT_START", activityName: "GDSRCPT_START"},
  position: {x: 25.0, y: 30.0},
  type:"start",
  parentNode: "parent_GDSRCPT_START",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_GDSRCPT_START_out_0_0",
  data: {obligationID: "0", objectType: "GDSRCPT"},
  position: {x: 215.0, y: 72.0},
  type:"obligation",
  parentNode: "parent_GDSRCPT_START",
  extent: "parent",
  draggable: true
  },{ 
  id: "parent_INVOICE_START",
  data: {},
  position: {x: -1200, y: 300},
  type:"group",
  style: {width: 240, height: 160}
  },{ 
  id: "INVOICE_START",
  data: {activityID: "INVOICE_START", activityName: "INVOICE_START"},
  position: {x: 25.0, y: 30.0},
  type:"start",
  parentNode: "parent_INVOICE_START",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_INVOICE_START_out_0_0",
  data: {obligationID: "0", objectType: "INVOICE"},
  position: {x: 215.0, y: 72.0},
  type:"obligation",
  parentNode: "parent_INVOICE_START",
  extent: "parent",
  draggable: true
  },{ 
  id: "parent_MATERIAL_START",
  data: {},
  position: {x: -2800, y: 0},
  type:"group",
  style: {width: 240, height: 160}
  },{ 
  id: "MATERIAL_START",
  data: {activityID: "MATERIAL_START", activityName: "MATERIAL_START"},
  position: {x: 25.0, y: 30.0},
  type:"start",
  parentNode: "parent_MATERIAL_START",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_MATERIAL_START_out_0_0",
  data: {obligationID: "0", objectType: "MATERIAL"},
  position: {x: 215.0, y: 72.0},
  type:"obligation",
  parentNode: "parent_MATERIAL_START",
  extent: "parent",
  draggable: true
  },{ 
  id: "parent_PURCHREQ_START",
  data: {},
  position: {x: -2800, y: 300},
  type:"group",
  style: {width: 240, height: 160}
  },{ 
  id: "PURCHREQ_START",
  data: {activityID: "PURCHREQ_START", activityName: "PURCHREQ_START"},
  position: {x: 25.0, y: 30.0},
  type:"start",
  parentNode: "parent_PURCHREQ_START",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_PURCHREQ_START_out_0_0",
  data: {obligationID: "0", objectType: "PURCHREQ"},
  position: {x: 215.0, y: 72.0},
  type:"obligation",
  parentNode: "parent_PURCHREQ_START",
  extent: "parent",
  draggable: true
  },{ 
  id: "parent_PURCHORD_START",
  data: {},
  position: {x: -2400, y: 300},
  type:"group",
  style: {width: 240, height: 160}
  },{ 
  id: "PURCHORD_START",
  data: {activityID: "PURCHORD_START", activityName: "PURCHORD_START"},
  position: {x: 25.0, y: 30.0},
  type:"start",
  parentNode: "parent_PURCHORD_START",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_PURCHORD_START_out_0_0",
  data: {obligationID: "0", objectType: "PURCHORD"},
  position: {x: 215.0, y: 72.0},
  type:"obligation",
  parentNode: "parent_PURCHORD_START",
  extent: "parent",
  draggable: true
  },{ 
  id: "parent_GDSRCPT_END",
  data: {},
  position: {x: 0, y: 0},
  type:"group",
  style: {width: 240, height: 160}
  },{ 
  id: "GDSRCPT_END",
  data: {activityID: "GDSRCPT_END", activityName: "GDSRCPT_END"},
  position: {x: 65.0, y: 30.0},
  type:"end",
  parentNode: "parent_GDSRCPT_END",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_GDSRCPT_END_in_0_0",
  data: {obligationID: "0", objectType: "GDSRCPT"},
  position: {x: 5.0, y: 72.0},
  type:"obligation",
  parentNode: "parent_GDSRCPT_END",
  extent: "parent",
  draggable: true
  },{ 
  id: "parent_INVOICE_END",
  data: {},
  position: {x: 0, y: 300},
  type:"group",
  style: {width: 240, height: 160}
  },{ 
  id: "INVOICE_END",
  data: {activityID: "INVOICE_END", activityName: "INVOICE_END"},
  position: {x: 65.0, y: 30.0},
  type:"end",
  parentNode: "parent_INVOICE_END",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_INVOICE_END_in_0_0",
  data: {obligationID: "0", objectType: "INVOICE"},
  position: {x: 5.0, y: 72.0},
  type:"obligation",
  parentNode: "parent_INVOICE_END",
  extent: "parent",
  draggable: true
  },{ 
  id: "parent_MATERIAL_END",
  data: {},
  position: {x: 0, y: 600},
  type:"group",
  style: {width: 240, height: 160}
  },{ 
  id: "MATERIAL_END",
  data: {activityID: "MATERIAL_END", activityName: "MATERIAL_END"},
  position: {x: 65.0, y: 30.0},
  type:"end",
  parentNode: "parent_MATERIAL_END",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_MATERIAL_END_in_0_0",
  data: {obligationID: "0", objectType: "MATERIAL"},
  position: {x: 5.0, y: 72.0},
  type:"obligation",
  parentNode: "parent_MATERIAL_END",
  extent: "parent",
  draggable: true
  },{ 
  id: "parent_PURCHREQ_END",
  data: {},
  position: {x: 0, y: 900},
  type:"group",
  style: {width: 240, height: 160}
  },{ 
  id: "PURCHREQ_END",
  data: {activityID: "PURCHREQ_END", activityName: "PURCHREQ_END"},
  position: {x: 65.0, y: 30.0},
  type:"end",
  parentNode: "parent_PURCHREQ_END",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_PURCHREQ_END_in_0_0",
  data: {obligationID: "0", objectType: "PURCHREQ"},
  position: {x: 5.0, y: 72.0},
  type:"obligation",
  parentNode: "parent_PURCHREQ_END",
  extent: "parent",
  draggable: true
  },{ 
  id: "parent_PURCHORD_END",
  data: {},
  position: {x: 0, y: 1200},
  type:"group",
  style: {width: 240, height: 160}
  },{ 
  id: "PURCHORD_END",
  data: {activityID: "PURCHORD_END", activityName: "PURCHORD_END"},
  position: {x: 65.0, y: 30.0},
  type:"end",
  parentNode: "parent_PURCHORD_END",
  extent: "parent",
  draggable: true
  },{ 
  id: "obl_PURCHORD_END_in_0_0",
  data: {obligationID: "0", objectType: "PURCHORD"},
  position: {x: 5.0, y: 72.0},
  type:"obligation",
  parentNode: "parent_PURCHORD_END",
  extent: "parent",
  draggable: true
  },
  ];

const initialEdges: Edge[] = [
  { 
    id: "edge_dep_Create_Purchase_Requisition_in_MATERIAL",
    source: "obl_Create_Purchase_Requisition_in_0_0",
    target: "Create_Purchase_Requisition",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Create_Purchase_Requisition_in_PURCHREQ",
    source: "obl_Create_Purchase_Requisition_in_0_1",
    target: "Create_Purchase_Requisition",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_obl_Create_Purchase_Requisition_in_0_1",
    source: "obl_Create_Purchase_Requisition_in_0_0",
    target: "obl_Create_Purchase_Requisition_in_0_1",
    sourceHandle: "binding_out",
    targetHandle: "binding_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Create_Purchase_Requisition_out_PURCHREQ",
    source: "Create_Purchase_Requisition",
    target: "obl_Create_Purchase_Requisition_out_0_0",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Create_Purchase_Requisition_out_MATERIAL",
    source: "Create_Purchase_Requisition",
    target: "obl_Create_Purchase_Requisition_out_0_1",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_obl_Create_Purchase_Requisition_out_0_1",
    source: "obl_Create_Purchase_Requisition_out_0_0",
    target: "obl_Create_Purchase_Requisition_out_0_1",
    sourceHandle: "binding_out",
    targetHandle: "binding_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Issue_Goods_Receipt_in_PURCHORD",
    source: "obl_Issue_Goods_Receipt_in_0_0",
    target: "Issue_Goods_Receipt",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Issue_Goods_Receipt_in_GDSRCPT",
    source: "obl_Issue_Goods_Receipt_in_0_1",
    target: "Issue_Goods_Receipt",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_obl_Issue_Goods_Receipt_in_0_1",
    source: "obl_Issue_Goods_Receipt_in_0_0",
    target: "obl_Issue_Goods_Receipt_in_0_1",
    sourceHandle: "binding_out",
    targetHandle: "binding_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Issue_Goods_Receipt_in_MATERIAL",
    source: "obl_Issue_Goods_Receipt_in_0_2",
    target: "Issue_Goods_Receipt",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_obl_Issue_Goods_Receipt_in_0_2",
    source: "obl_Issue_Goods_Receipt_in_0_1",
    target: "obl_Issue_Goods_Receipt_in_0_2",
    sourceHandle: "binding_out",
    targetHandle: "binding_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Issue_Goods_Receipt_out_GDSRCPT",
    source: "Issue_Goods_Receipt",
    target: "obl_Issue_Goods_Receipt_out_0_0",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Issue_Goods_Receipt_out_PURCHORD",
    source: "Issue_Goods_Receipt",
    target: "obl_Issue_Goods_Receipt_out_0_1",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_obl_Issue_Goods_Receipt_out_0_1",
    source: "obl_Issue_Goods_Receipt_out_0_0",
    target: "obl_Issue_Goods_Receipt_out_0_1",
    sourceHandle: "binding_out",
    targetHandle: "binding_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Issue_Goods_Receipt_out_MATERIAL",
    source: "Issue_Goods_Receipt",
    target: "obl_Issue_Goods_Receipt_out_0_2",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_obl_Issue_Goods_Receipt_out_0_2",
    source: "obl_Issue_Goods_Receipt_out_0_1",
    target: "obl_Issue_Goods_Receipt_out_0_2",
    sourceHandle: "binding_out",
    targetHandle: "binding_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Issue_Goods_Receipt_out_MATERIAL",
    source: "Issue_Goods_Receipt",
    target: "obl_Issue_Goods_Receipt_out_0_3",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_obl_Issue_Goods_Receipt_out_0_3",
    source: "obl_Issue_Goods_Receipt_out_0_2",
    target: "obl_Issue_Goods_Receipt_out_0_3",
    sourceHandle: "binding_out",
    targetHandle: "binding_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Receive_Invoice_in_PURCHORD",
    source: "obl_Receive_Invoice_in_0_0",
    target: "Receive_Invoice",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Receive_Invoice_in_INVOICE",
    source: "obl_Receive_Invoice_in_0_1",
    target: "Receive_Invoice",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_obl_Receive_Invoice_in_0_1",
    source: "obl_Receive_Invoice_in_0_0",
    target: "obl_Receive_Invoice_in_0_1",
    sourceHandle: "binding_out",
    targetHandle: "binding_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Receive_Invoice_out_PURCHORD",
    source: "Receive_Invoice",
    target: "obl_Receive_Invoice_out_0_0",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Receive_Invoice_out_INVOICE",
    source: "Receive_Invoice",
    target: "obl_Receive_Invoice_out_0_1",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_obl_Receive_Invoice_out_0_1",
    source: "obl_Receive_Invoice_out_0_0",
    target: "obl_Receive_Invoice_out_0_1",
    sourceHandle: "binding_out",
    targetHandle: "binding_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Receive_Goods_in_MATERIAL",
    source: "obl_Receive_Goods_in_0_0",
    target: "Receive_Goods",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Receive_Goods_in_PURCHORD",
    source: "obl_Receive_Goods_in_0_1",
    target: "Receive_Goods",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_obl_Receive_Goods_in_0_1",
    source: "obl_Receive_Goods_in_0_0",
    target: "obl_Receive_Goods_in_0_1",
    sourceHandle: "binding_out",
    targetHandle: "binding_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Receive_Goods_in_GDSRCPT",
    source: "obl_Receive_Goods_in_0_2",
    target: "Receive_Goods",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_obl_Receive_Goods_in_0_2",
    source: "obl_Receive_Goods_in_0_1",
    target: "obl_Receive_Goods_in_0_2",
    sourceHandle: "binding_out",
    targetHandle: "binding_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Receive_Goods_out_PURCHORD",
    source: "Receive_Goods",
    target: "obl_Receive_Goods_out_0_0",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Receive_Goods_out_MATERIAL",
    source: "Receive_Goods",
    target: "obl_Receive_Goods_out_0_1",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_obl_Receive_Goods_out_0_1",
    source: "obl_Receive_Goods_out_0_0",
    target: "obl_Receive_Goods_out_0_1",
    sourceHandle: "binding_out",
    targetHandle: "binding_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Receive_Goods_out_GDSRCPT",
    source: "Receive_Goods",
    target: "obl_Receive_Goods_out_0_2",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_obl_Receive_Goods_out_0_2",
    source: "obl_Receive_Goods_out_0_1",
    target: "obl_Receive_Goods_out_0_2",
    sourceHandle: "binding_out",
    targetHandle: "binding_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Plan_Goods_Issue_in_MATERIAL",
    source: "obl_Plan_Goods_Issue_in_0_0",
    target: "Plan_Goods_Issue",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Plan_Goods_Issue_out_MATERIAL",
    source: "Plan_Goods_Issue",
    target: "obl_Plan_Goods_Issue_out_0_0",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Verify_Material_in_MATERIAL",
    source: "obl_Verify_Material_in_0_0",
    target: "Verify_Material",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Verify_Material_out_MATERIAL",
    source: "Verify_Material",
    target: "obl_Verify_Material_out_0_0",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Goods_Issue_in_MATERIAL",
    source: "obl_Goods_Issue_in_0_0",
    target: "Goods_Issue",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Goods_Issue_in_MATERIAL",
    source: "obl_Goods_Issue_in_0_1",
    target: "Goods_Issue",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_obl_Goods_Issue_in_0_1",
    source: "obl_Goods_Issue_in_0_0",
    target: "obl_Goods_Issue_in_0_1",
    sourceHandle: "binding_out",
    targetHandle: "binding_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Goods_Issue_out_MATERIAL",
    source: "Goods_Issue",
    target: "obl_Goods_Issue_out_0_0",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Create_Purchase_Order_in_PURCHREQ",
    source: "obl_Create_Purchase_Order_in_0_0",
    target: "Create_Purchase_Order",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Create_Purchase_Order_in_MATERIAL",
    source: "obl_Create_Purchase_Order_in_0_1",
    target: "Create_Purchase_Order",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_obl_Create_Purchase_Order_in_0_1",
    source: "obl_Create_Purchase_Order_in_0_0",
    target: "obl_Create_Purchase_Order_in_0_1",
    sourceHandle: "binding_out",
    targetHandle: "binding_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Create_Purchase_Order_in_PURCHORD",
    source: "obl_Create_Purchase_Order_in_0_2",
    target: "Create_Purchase_Order",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_obl_Create_Purchase_Order_in_0_2",
    source: "obl_Create_Purchase_Order_in_0_1",
    target: "obl_Create_Purchase_Order_in_0_2",
    sourceHandle: "binding_out",
    targetHandle: "binding_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Create_Purchase_Order_out_PURCHORD",
    source: "Create_Purchase_Order",
    target: "obl_Create_Purchase_Order_out_0_0",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Create_Purchase_Order_out_MATERIAL",
    source: "Create_Purchase_Order",
    target: "obl_Create_Purchase_Order_out_0_1",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_obl_Create_Purchase_Order_out_0_1",
    source: "obl_Create_Purchase_Order_out_0_0",
    target: "obl_Create_Purchase_Order_out_0_1",
    sourceHandle: "binding_out",
    targetHandle: "binding_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Create_Purchase_Order_out_PURCHREQ",
    source: "Create_Purchase_Order",
    target: "obl_Create_Purchase_Order_out_0_2",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_obl_Create_Purchase_Order_out_0_2",
    source: "obl_Create_Purchase_Order_out_0_1",
    target: "obl_Create_Purchase_Order_out_0_2",
    sourceHandle: "binding_out",
    targetHandle: "binding_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Clear_Invoice_in_INVOICE",
    source: "obl_Clear_Invoice_in_0_0",
    target: "Clear_Invoice",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Clear_Invoice_in_PURCHORD",
    source: "obl_Clear_Invoice_in_0_1",
    target: "Clear_Invoice",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_obl_Clear_Invoice_in_0_1",
    source: "obl_Clear_Invoice_in_0_0",
    target: "obl_Clear_Invoice_in_0_1",
    sourceHandle: "binding_out",
    targetHandle: "binding_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Clear_Invoice_in_GDSRCPT",
    source: "obl_Clear_Invoice_in_0_2",
    target: "Clear_Invoice",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_obl_Clear_Invoice_in_0_2",
    source: "obl_Clear_Invoice_in_0_1",
    target: "obl_Clear_Invoice_in_0_2",
    sourceHandle: "binding_out",
    targetHandle: "binding_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Clear_Invoice_out_GDSRCPT",
    source: "Clear_Invoice",
    target: "obl_Clear_Invoice_out_0_0",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Clear_Invoice_out_INVOICE",
    source: "Clear_Invoice",
    target: "obl_Clear_Invoice_out_0_1",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_obl_Clear_Invoice_out_0_1",
    source: "obl_Clear_Invoice_out_0_0",
    target: "obl_Clear_Invoice_out_0_1",
    sourceHandle: "binding_out",
    targetHandle: "binding_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Clear_Invoice_out_PURCHORD",
    source: "Clear_Invoice",
    target: "obl_Clear_Invoice_out_0_2",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_obl_Clear_Invoice_out_0_2",
    source: "obl_Clear_Invoice_out_0_1",
    target: "obl_Clear_Invoice_out_0_2",
    sourceHandle: "binding_out",
    targetHandle: "binding_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_GDSRCPT_START_out_GDSRCPT",
    source: "GDSRCPT_START",
    target: "obl_GDSRCPT_START_out_0_0",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_INVOICE_START_out_INVOICE",
    source: "INVOICE_START",
    target: "obl_INVOICE_START_out_0_0",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_MATERIAL_START_out_MATERIAL",
    source: "MATERIAL_START",
    target: "obl_MATERIAL_START_out_0_0",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_PURCHREQ_START_out_PURCHREQ",
    source: "PURCHREQ_START",
    target: "obl_PURCHREQ_START_out_0_0",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_PURCHORD_START_out_PURCHORD",
    source: "PURCHORD_START",
    target: "obl_PURCHORD_START_out_0_0",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_GDSRCPT_END_in_GDSRCPT",
    source: "obl_GDSRCPT_END_in_0_0",
    target: "GDSRCPT_END",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_INVOICE_END_in_INVOICE",
    source: "obl_INVOICE_END_in_0_0",
    target: "INVOICE_END",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_MATERIAL_END_in_MATERIAL",
    source: "obl_MATERIAL_END_in_0_0",
    target: "MATERIAL_END",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_PURCHREQ_END_in_PURCHREQ",
    source: "obl_PURCHREQ_END_in_0_0",
    target: "PURCHREQ_END",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_PURCHORD_END_in_PURCHORD",
    source: "obl_PURCHORD_END_in_0_0",
    target: "PURCHORD_END",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Create_Purchase_Requisition_in_MATERIAL",
    source: "obl_MATERIAL_START_out_0_0",
    target: "obl_Create_Purchase_Requisition_in_0_0",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Create_Purchase_Requisition_in_PURCHREQ",
    source: "obl_PURCHREQ_START_out_0_0",
    target: "obl_Create_Purchase_Requisition_in_0_1",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Issue_Goods_Receipt_in_PURCHORD",
    source: "obl_Receive_Goods_out_0_0",
    target: "obl_Issue_Goods_Receipt_in_0_0",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Issue_Goods_Receipt_in_GDSRCPT",
    source: "obl_Receive_Goods_out_0_2",
    target: "obl_Issue_Goods_Receipt_in_0_1",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Issue_Goods_Receipt_in_MATERIAL",
    source: "obl_Receive_Goods_out_0_1",
    target: "obl_Issue_Goods_Receipt_in_0_2",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Receive_Invoice_in_PURCHORD",
    source: "obl_Issue_Goods_Receipt_out_0_1",
    target: "obl_Receive_Invoice_in_0_0",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Receive_Invoice_in_INVOICE",
    source: "obl_INVOICE_START_out_0_0",
    target: "obl_Receive_Invoice_in_0_1",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Receive_Goods_in_MATERIAL",
    source: "obl_Create_Purchase_Order_out_0_1",
    target: "obl_Receive_Goods_in_0_0",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Receive_Goods_in_PURCHORD",
    source: "obl_Create_Purchase_Order_out_0_0",
    target: "obl_Receive_Goods_in_0_1",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Receive_Goods_in_GDSRCPT",
    source: "obl_GDSRCPT_START_out_0_0",
    target: "obl_Receive_Goods_in_0_2",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Plan_Goods_Issue_in_MATERIAL",
    source: "obl_Issue_Goods_Receipt_out_0_3",
    target: "obl_Plan_Goods_Issue_in_0_0",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Verify_Material_in_MATERIAL",
    source: "obl_Issue_Goods_Receipt_out_0_3",
    target: "obl_Verify_Material_in_0_0",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Goods_Issue_in_MATERIAL",
    source: "obl_Verify_Material_out_0_0",
    target: "obl_Goods_Issue_in_0_0",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Goods_Issue_in_MATERIAL",
    source: "obl_Plan_Goods_Issue_out_0_0",
    target: "obl_Goods_Issue_in_0_0",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Create_Purchase_Order_in_PURCHREQ",
    source: "obl_Create_Purchase_Requisition_out_0_0",
    target: "obl_Create_Purchase_Order_in_0_0",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Create_Purchase_Order_in_MATERIAL",
    source: "obl_Create_Purchase_Requisition_out_0_1",
    target: "obl_Create_Purchase_Order_in_0_1",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Create_Purchase_Order_in_PURCHORD",
    source: "obl_PURCHORD_START_out_0_0",
    target: "obl_Create_Purchase_Order_in_0_2",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Clear_Invoice_in_INVOICE",
    source: "obl_Receive_Invoice_out_0_1",
    target: "obl_Clear_Invoice_in_0_0",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Clear_Invoice_in_PURCHORD",
    source: "obl_Receive_Invoice_out_0_0",
    target: "obl_Clear_Invoice_in_0_1",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_Clear_Invoice_in_GDSRCPT",
    source: "obl_Issue_Goods_Receipt_out_0_0",
    target: "obl_Clear_Invoice_in_0_2",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_GDSRCPT_END_in_GDSRCPT",
    source: "obl_Clear_Invoice_out_0_0",
    target: "obl_GDSRCPT_END_in_0_0",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_INVOICE_END_in_INVOICE",
    source: "obl_Clear_Invoice_out_0_1",
    target: "obl_INVOICE_END_in_0_0",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_MATERIAL_END_in_MATERIAL",
    source: "obl_Goods_Issue_out_0_0",
    target: "obl_MATERIAL_END_in_0_0",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_PURCHREQ_END_in_PURCHREQ",
    source: "obl_Create_Purchase_Order_out_0_2",
    target: "obl_PURCHREQ_END_in_0_0",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "custom",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },{ 
    id: "edge_dep_PURCHORD_END_in_PURCHORD",
    source: "obl_Clear_Invoice_out_0_2",
    target: "obl_PURCHORD_END_in_0_0",
    sourceHandle: "dependency_out",
    targetHandle: "dependency_in",
    type: "smart",
    style: { strokeWidth: 2, stroke: "#FFFFFF" }
    },
];

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
      fitView
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
