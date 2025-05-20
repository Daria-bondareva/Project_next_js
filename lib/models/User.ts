import mongoose from "mongoose";
import EventModel from "./Event";
import bcrypt from "bcrypt";

const UserSchema = new mongoose.Schema({
  username: { type: String, required: true, unique: true },
  email: { type: String, required: true },
  passwordHash: { type: String, required: true },
});

UserSchema.pre("findOneAndDelete", async function (next) {
  const user = await this.model.findOne(this.getFilter());
  if (user) {
    await EventModel.deleteMany({ userId: user._id });
  }
  next();
});

// Метод для перевірки паролю
UserSchema.methods.comparePassword = function (password: string) {
  return bcrypt.compare(password, this.passwordHash);
};

export default mongoose.models.User || mongoose.model("User", UserSchema);
