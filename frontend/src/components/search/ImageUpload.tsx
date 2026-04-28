import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, X } from 'lucide-react'
import { useSearchStore } from '../../stores/searchStore'

const ImageUpload = () => {
  const { queryImage, setQueryImage } = useSearchStore()
  const [preview, setPreview] = useState<string | null>(null)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (file) {
      setQueryImage(file)
      const reader = new FileReader()
      reader.onload = () => {
        setPreview(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }, [setQueryImage])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.webp']
    },
    multiple: false
  })

  const removeImage = (e: React.MouseEvent) => {
    e.stopPropagation()
    setQueryImage(null)
    setPreview(null)
  }

  return (
    <div 
      {...getRootProps()} 
      className={`
        relative border-2 border-dashed rounded-lg p-4 transition-colors cursor-pointer
        ${isDragActive ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50'}
        ${preview ? 'p-0 h-40 overflow-hidden' : 'h-32 flex flex-col items-center justify-center'}
      `}
    >
      <input {...getInputProps()} />
      
      {preview ? (
        <div className="relative w-full h-full group">
          <img src={preview} alt="Query" className="w-full h-full object-cover" />
          <button 
            onClick={removeImage}
            className="absolute top-2 right-2 p-1 bg-background/80 rounded-full hover:bg-background text-foreground"
          >
            <X size={16} />
          </button>
        </div>
      ) : (
        <>
          <Upload className="w-8 h-8 mb-2 text-muted-foreground" />
          <p className="text-xs text-center text-muted-foreground">
            Drag & drop query image<br />or click to browse
          </p>
        </>
      )}
    </div>
  )
}

export default ImageUpload
