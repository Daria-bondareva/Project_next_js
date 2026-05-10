import mongoose from "mongoose";

const EventSchema = new mongoose.Schema({
  title: { type: String, required: true },
  date: { type: Date, required: true },
  userId: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
  participants: [{ type: mongoose.Schema.Types.ObjectId, ref: "User" }], // Додано

  tags: [{ type: String }], 
  description: { type: String },
});


export default mongoose.models.Event || mongoose.model("Event", EventSchema);
