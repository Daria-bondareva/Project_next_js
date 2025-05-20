import mongoose, { Schema, model, models } from "mongoose";

const reportSchema = new Schema(
  {
    reporterId: { type: Schema.Types.ObjectId, ref: "User", required: true },
    targetType: { type: String, enum: ["User", "Event"], required: true },
    targetId: { type: Schema.Types.ObjectId, required: true },
    reason: { type: String, required: true },
  },
  { timestamps: true }
);

const Report = models.Report || model("Report", reportSchema);
export default Report;
