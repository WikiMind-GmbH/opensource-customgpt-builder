import { useEffect, useState } from "react";
import "./CreateOrEditCustomGPT.css";
import { CreateOrEditCustomGPTForm } from "../interfaces/interfaces";
import { useNavigate, useParams } from "react-router-dom";
import {
  CreateOrEditCustomGPTStatus,
  CustomGpTsService,
  CustomGptToCreateOrEdit,
  ExistingCustomGPT,
} from "../client";

export default function CreateOrEditCustomGPT() {
  const { idOfCustomGptOrUndefined } = useParams<{
    idOfCustomGptOrUndefined?: string;
  }>();
  const [form, setForm] = useState<CreateOrEditCustomGPTForm>({
    custom_gpt_name: "",
    custom_gpt_description: "",
    custom_gpt_instructions: "",
  });
  const navigate = useNavigate();
  // ToDo: add Endpoint for this, functions
  function handleChangeToFormFields(e) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }
  
  async function createOrEditCustomGPT() {
    if (idOfCustomGptOrUndefined === undefined) {
      const body: CustomGptToCreateOrEdit = { custom_gpt_id: null, ...form };
      const res: CreateOrEditCustomGPTStatus =
        await CustomGpTsService.createOrEditCustomGpt(body);
      navigate(`/createOrEditCustomGPT/${res.custom_gpt_id}`);
    } else {
      const body: CustomGptToCreateOrEdit = {
        custom_gpt_id: Number(idOfCustomGptOrUndefined),
        ...form,
      };
      const res: CreateOrEditCustomGPTStatus =
        await CustomGpTsService.createOrEditCustomGpt(body);
    }
  }

  useEffect(() => {
    async function load() {
      if (idOfCustomGptOrUndefined) {
        const infosOfCustomGpt: ExistingCustomGPT =
          await CustomGpTsService.getCustomGptInfos(
            Number(idOfCustomGptOrUndefined)
          ); // ⬅️ adjust endpoint
        const customGptInfosForForms: CreateOrEditCustomGPTForm = (({
          custom_gpt_name,
          custom_gpt_description,
          custom_gpt_instructions,
        }: ExistingCustomGPT) => ({
          custom_gpt_name,
          custom_gpt_description,
          custom_gpt_instructions,
        }))(infosOfCustomGpt);
        setForm(customGptInfosForForms);
      }
    }
    load();
  }, []);

  return (
    <div className="editor">
      <label className="field">
        <span className="title">Name</span>
        <input
          name="custom_gpt_name"
          type="text"
          value={form.custom_gpt_name}
          onChange={handleChangeToFormFields}
          className="small"
        />
      </label>

      <label className="field">
        <span className="title">Description</span>
        <textarea
          name="custom_gpt_description"
          rows={4}
          value={form.custom_gpt_description}
          onChange={handleChangeToFormFields}
          className="medium"
        />
      </label>

      <label className="field">
        <span className="title">Instruction</span>
        <textarea
          name="custom_gpt_instructions"
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
