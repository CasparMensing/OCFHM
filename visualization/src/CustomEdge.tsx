import { BezierEdge, EdgeProps } from "reactflow";

export default function CustomEdge(props: EdgeProps) {
  // we are using the default bezier edge when source and target ids are different
  if (props.data.start_activity != props.data.end_activity) {
    return <BezierEdge {...props} />;
  }

  const { sourceX, sourceY, targetX, targetY, id, markerEnd } = props;
  const radiusX = (sourceX - targetX) * 0.6;
  const radiusY = 50;
  const edgePath = `M ${sourceX - 5} ${sourceY} A ${radiusX} ${radiusY} 0 1 0 ${
    targetX + 2
  } ${targetY}`;

  return (
    <path
      id={id}
      className="react-flow__edge-path"
      d={edgePath}
      markerEnd={markerEnd}
      style = {props.style}
    />
  );
}
