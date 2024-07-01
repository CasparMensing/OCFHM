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
        fontSize: 80,
        ...styles
      }}
    >
      <Handle
        type="target"
        position={Position.Left}
        id="dependency_in"
      />
      ⏹
    </div>
    </>
  );
};
