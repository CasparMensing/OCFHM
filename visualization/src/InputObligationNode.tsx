import React from "react";

import { Handle, Position } from "reactflow";

export default ({ data, styles }: any) => {
  return (
    <div className={data.objectType}
    style={{
        width: "16px",
        height: "16px",
        borderRadius: "50%",
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
      <Handle
        type="target"
        position={Position.Top}
        id="binding_in"
      />
      <div style={{color:'#000000'}}>
        {data.obligationID}
      </div>
      <Handle
        type="source"
        position={Position.Right}
        id="dependency_out"
      />
      <Handle
        type="source"
        position={Position.Bottom}
        id="binding_out"
      />
    </div>
  );
};
