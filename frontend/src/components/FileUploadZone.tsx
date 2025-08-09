// FileUploadZone.tsx
import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import './FileUploadZone.css'
import { Body_addFilesToGpt, CustomGpTsService } from '../client'

export default function FileUploadZone({
  gptId,
}: {
  gptId: number,
}) {
  const [progress, setProgress] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Read and split your env var into [".jpg", ".png", ".pdf", ...]
  const raw = import.meta.env.UPLOAD_ALLOWED_SUFFIXES || ''
  const allowedSuffixes = raw
    .split(',')
    .map((s) => s.trim())
    .filter((s) => s.startsWith('.') && s.length > 1)

  // Build dropzone accept map: { ".jpg": [], ".pdf": [], ... }
  const accept = allowedSuffixes.reduce<Record<string, string[]>>(
    (acc, ext) => {
      acc[ext] = []
      return acc
    },
    {}
  )

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      setError(null)
      setProgress(0)

      const payload:Body_addFilesToGpt  = {
        files: acceptedFiles as Blob[],
      }

      try {
        await CustomGpTsService.addFilesToGpt(
          gptId,
          payload
        )
        setProgress(null)
      } catch (err: any) {
        const msg =
          err?.body?.detail ?? err?.message ?? 'Upload failed'
        setError(msg)
        alert(msg)
        setProgress(null)
      }
    },
    []
  )

  const {
    getRootProps,
    getInputProps,
    isDragActive,
    fileRejections,
  } = useDropzone({
    onDrop,
    accept,
    multiple: true,
    maxFiles: 50,
    maxSize: Number(import.meta.env.UPLOAD_MAX_FILE_SIZE),
  })

  return (
    <div
      {...getRootProps()}
      className={`upload-zone ${isDragActive ? 'drag-active' : ''}`}
    >
      <input {...getInputProps()} />

      <p>
        Drag &amp; drop{' '}
        <strong>
          {allowedSuffixes.length
            ? allowedSuffixes.join(', ')
            : 'files'}
        </strong>{' '}
        here, or click to select
      </p>

      {progress !== null && (
        <div className="progress-wrapper">
          <div
            className="progress-bar"
            style={{ width: `${progress}%` }}
          />
          <small>{progress}%</small>
        </div>
      )}

      {error && <p className="upload-error">{error}</p>}

      {fileRejections.length > 0 && (
        <p className="upload-error">
          Some files were rejected (too many, too large, or wrong
          type).
        </p>
      )}
    </div>
  )
}
