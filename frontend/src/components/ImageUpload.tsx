import { useState, useCallback } from "react";
import { Upload, Image as ImageIcon, X } from "lucide-react";
import { cn } from "@/lib/utils";

interface ImageUploadProps {
  onImageSelect: (file: File) => void;
  isLoading?: boolean;
  className?: string;
}

export function ImageUpload({ onImageSelect, isLoading, className }: ImageUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDragIn = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
      setIsDragging(true);
    }
  }, []);

  const handleDragOut = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      if (file.type.startsWith("image/")) {
        handleFile(file);
      }
    }
  }, []);

  const handleFile = (file: File) => {
    setSelectedFile(file);
    const reader = new FileReader();
    reader.onload = () => {
      setPreview(reader.result as string);
    };
    reader.readAsDataURL(file);
    onImageSelect(file);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFile(e.target.files[0]);
    }
  };

  const clearImage = () => {
    setPreview(null);
    setSelectedFile(null);
  };

  if (preview) {
    return (
      <div className={cn("relative", className)}>
        <div className="polaroid-card max-w-sm mx-auto">
          <div className="relative aspect-square overflow-hidden rounded-sm">
            <img
              src={preview}
              alt="Selected flower"
              className="w-full h-full object-cover"
            />
            {isLoading && (
              <div className="absolute inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center">
                <div className="flex flex-col items-center gap-3">
                  <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                  <p className="text-sm text-muted-foreground">Identifying flower...</p>
                </div>
              </div>
            )}
          </div>
          {!isLoading && (
            <button
              onClick={clearImage}
              className="absolute -top-2 -right-2 w-8 h-8 bg-card rounded-full shadow-card flex items-center justify-center hover:bg-muted transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          )}
          {selectedFile && (
            <p className="mt-3 text-center text-sm text-muted-foreground font-serif italic">
              {selectedFile.name}
            </p>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className={className}>
      <label
        htmlFor="flower-upload"
        className={cn(
          "upload-zone flex flex-col items-center justify-center cursor-pointer min-h-[280px]",
          isDragging && "upload-zone-active"
        )}
        onDragEnter={handleDragIn}
        onDragLeave={handleDragOut}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <div className="flex flex-col items-center gap-4">
          <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">
            {isDragging ? (
              <ImageIcon className="w-8 h-8 text-primary" />
            ) : (
              <Upload className="w-8 h-8 text-primary" />
            )}
          </div>
          <div className="text-center">
            <p className="text-lg font-serif font-medium text-foreground">
              {isDragging ? "Drop your image here" : "Upload a flower photo"}
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              Drag and drop or click to browse
            </p>
          </div>
          <p className="text-xs text-muted-foreground">
            Supports JPEG, PNG, WebP (max 5MB)
          </p>
        </div>
        <input
          id="flower-upload"
          type="file"
          accept="image/jpeg,image/png,image/webp"
          onChange={handleInputChange}
          className="hidden"
        />
      </label>
    </div>
  );
}