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
import FileUploadZone from "../components/FileUploadZone";

export default function CreateOrEditCustomGPT() {
  const { idOfCustomGptOrUndefinedStr } = useParams<{
    idOfCustomGptOrUndefinedStr?: string;
  }>();

  const [form, setForm] = useState<CreateOrEditCustomGPTForm>({
    custom_gpt_name: "",
    custom_gpt_description: "",
    custom_gpt_instructions: "",
  });
const [files, setFiles] = useState<string[]>([]);

  const navigate = useNavigate();
  // ToDo: add Endpoint for this, functions
  function handleChangeToFormFields(e) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function createOrEditCustomGPT() {
    if (idOfCustomGptOrUndefinedStr === undefined) {
      const body: CustomGptToCreateOrEdit = { custom_gpt_id: null, ...form };
      const res: CreateOrEditCustomGPTStatus =
        await CustomGpTsService.createOrEditCustomGpt(body);
      navigate(`/createOrEditCustomGPT/${res.custom_gpt_id}`);
    } else {
      const body: CustomGptToCreateOrEdit = {
        custom_gpt_id: Number(idOfCustomGptOrUndefinedStr),
        ...form,
      };
      const res: CreateOrEditCustomGPTStatus =
        await CustomGpTsService.createOrEditCustomGpt(body);
    }
  }

  useEffect(() => {
    async function load() {
      if (idOfCustomGptOrUndefinedStr) {
        const files: string[] = await CustomGpTsService.listFilesToGpt(Number(idOfCustomGptOrUndefinedStr))
        setFiles(files)
        const infosOfCustomGpt: ExistingCustomGPT =
          await CustomGpTsService.getCustomGptInfos(
            //ToDo: display "does not exist" page if customgpt does not exist
            Number(idOfCustomGptOrUndefinedStr)
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
  }, [idOfCustomGptOrUndefinedStr]);

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
      {idOfCustomGptOrUndefinedStr ? (
        <div>
          <FileUploadZone gptId={Number(idOfCustomGptOrUndefinedStr)} />
          <ul>
            {files.length > 0 ? (
              files.map((name) => (
                <li key={name}>{name}</li>
              ))
            ) : (
              <li>No files available</li> 
            )}
          </ul>
        </div>
        ) : (
          <p>You can upload files once a customGpt is created</p>
        )
      }
      </div>
  );
}
