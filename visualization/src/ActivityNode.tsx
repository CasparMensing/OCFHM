import React from "react";

import { Handle, Position, NodeToolbar } from "reactflow";

export default ({ data, styles }: any) => {
  return (
    <>
    <NodeToolbar>
      <div style={{background:'rgba(255,255,255,0.6)', color: '#000'}}>
        {data.objectTypes.join(', ')}
      </div>
    </NodeToolbar>
    <div className={data.activityID}
    style={{
        width: "150px",
        height: "100px",
        borderRadius: "5px",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        ...styles
      }}
    >
      <Handle
        type="target"
        position={Position.Left}
        id="dependency_in"
      />
      <div style={{width: "120px", color:'#000000', background:'rgba(255,255,255,0.3)', verticalAlign:'middle', lineHeight:'25px', padding:"5px"}}>
        <div className="container">
          {data.activityName}
        </div>
      </div>
      <Handle
        type="source"
        position={Position.Right}
        id="dependency_out"
      />
    </div>
    </>
  );
};
