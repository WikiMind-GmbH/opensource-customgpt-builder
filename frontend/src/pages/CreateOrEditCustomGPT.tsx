import { useState } from "react";
import "./CreateOrEditCustomGPT.css";
import { CreateOrEditCustomGPTForm } from "../interfaces/interfaces";
import { useNavigate, useParams } from "react-router-dom";
import {
  CreateCustomGPTResponse,
  CustomGptService,
  CustomGptToCreate,
} from "../client";

export default function CreateOrEditCustomGPT() {
  const { idOfCustomGPT } = useParams<{ idOfCustomGPT?: string }>();
  const [form, setForm] = useState<CustomGptToCreate>({
    custom_gpt_name: "",
    custom_gpt_description: "",
    custom_gpt_instructions: "",
  });
  // ToDo: add Endpoint for this, functions
  function handleChangeToFormFields(e) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function createOrEditCustomGPT() {
    console.log("Saving…", form);
    alert("Changes saved (check console)");
    if (idOfCustomGPT == null) {
      // call the createCustomGPT endpoint
      const res: CreateCustomGPTResponse =
        await CustomGptService.createCustomGptCreateCustomGptPost(form);
      // const navigate = useNavigate();
      // navigate(`/createCustomGPTs/${res.custom_gpt_id}`);
      // show feedback
    } else {
      // call editCustomGPT endpoint
      // show feedback
    }
  }

  return (
    <div className="editor">
      <label className="field">
        <span className="title">Name</span>
        <input
          name="name"
          type="text"
          value={form.custom_gpt_name}
          onChange={handleChangeToFormFields}
          className="small"
        />
      </label>

      <label className="field">
        <span className="title">Description</span>
        <textarea
          name="description"
          rows={4}
          value={form.custom_gpt_description}
          onChange={handleChangeToFormFields}
          className="medium"
        />
      </label>

      <label className="field">
        <span className="title">Instruction</span>
        <textarea
          name="instruction"
          rows={8}
          value={form.custom_gpt_instructions}
          onChange={handleChangeToFormFields}
          className="large"
        />
      </label>

      <button className="save-btn" onClick={createOrEditCustomGPT}>
        Save changes
      </button>
    </div>
  );
}
