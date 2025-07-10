import { useState } from "react";
import "./CreateOrEditCustomGPT.css"
import { CreateOrEditCustomGPTForm } from "../interfaces/interfaces";
import { useNavigate, useParams } from "react-router-dom";



export default function CreateOrEditCustomGPT(){
    const { idOfCustomGPT } = useParams<{ idOfCustomGPT?: string }>();
    const [form, setForm] = useState<CreateOrEditCustomGPTForm>({
    custom_gpt_name: "",
    description: "",
    instruction: "",
  });
  // ToDo: add Endpoint for this, functions
  function handleChangeToFormFields(e) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  function createOrEditCustomGPT() {
    console.log("Saving…", form);
    alert("Changes saved (check console)");
    if (idOfCustomGPT== null){
    // call the createCustomGPT endpoint
    // const res = await createOrEditCustomGPT()
    // const navigate = useNavigate();
    // navigate(`/createCustomGPTs/${res.idOfChat}`);
    // show feedback
    } else{
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
          value={form.description}
          onChange={handleChangeToFormFields}
          className="medium"
        />
      </label>

      <label className="field">
        <span className="title">Instruction</span>
        <textarea
          name="instruction"
          rows={8}
          value={form.instruction}
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