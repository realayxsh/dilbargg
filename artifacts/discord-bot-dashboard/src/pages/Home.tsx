import React, { useState, useRef, useEffect } from "react";
import { useGetBotProfile, useUpdateBotAvatar, useUpdateBotBanner, getGetBotProfileQueryKey } from "@workspace/api-client-react";
import { useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/hooks/use-toast";
import { Upload, Image as ImageIcon, AlertCircle } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

function AvatarUploader({ botProfile }: { botProfile: any }) {
  const [previewUri, setPreviewUri] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const updateAvatar = useUpdateBotAvatar();

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const dataUri = event.target?.result as string;
      setPreviewUri(dataUri);
    };
    reader.readAsDataURL(file);
  };

  const handleSave = () => {
    if (!previewUri) return;

    updateAvatar.mutate({ data: { imageDataUri: previewUri } }, {
      onSuccess: () => {
        toast({
          title: "Avatar updated",
          description: "Your bot's avatar has been successfully updated.",
        });
        setPreviewUri(null);
        queryClient.invalidateQueries({ queryKey: getGetBotProfileQueryKey() });
      },
      onError: (error: any) => {
        toast({
          title: "Update failed",
          description: error.error || "An error occurred while updating the avatar.",
          variant: "destructive",
        });
      }
    });
  };

  const handleCancel = () => {
    setPreviewUri(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const displayUrl = previewUri || botProfile.avatarUrl;

  return (
    <Card className="border-border/50 shadow-md">
      <CardHeader>
        <CardTitle className="text-xl">Avatar</CardTitle>
        <CardDescription>
          Update your bot's profile picture. We recommend an image of at least 512x512 pixels.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col md:flex-row gap-6 items-center md:items-start">
          <div className="relative group">
            <div className="w-32 h-32 rounded-full overflow-hidden border-4 border-background shadow-lg bg-muted flex items-center justify-center">
              {displayUrl ? (
                <img src={displayUrl} alt="Bot Avatar" className="w-full h-full object-cover" data-testid="img-avatar-preview" />
              ) : (
                <ImageIcon className="w-12 h-12 text-muted-foreground opacity-50" />
              )}
            </div>
            {!previewUri && (
              <Button 
                size="icon" 
                className="absolute bottom-0 right-0 rounded-full w-10 h-10 shadow-md"
                onClick={() => fileInputRef.current?.click()}
                data-testid="button-select-avatar"
              >
                <Upload className="w-4 h-4" />
              </Button>
            )}
          </div>
          <div className="flex-1 space-y-4 text-center md:text-left">
            <div>
              <h3 className="font-semibold text-lg">{botProfile.username}</h3>
              <p className="text-sm text-muted-foreground">#{botProfile.discriminator}</p>
            </div>
            
            <input 
              type="file" 
              accept="image/*" 
              className="hidden" 
              ref={fileInputRef} 
              onChange={handleFileSelect} 
              data-testid="input-avatar-file"
            />
            
            {!previewUri ? (
              <Button variant="outline" onClick={() => fileInputRef.current?.click()}>
                Choose Image
              </Button>
            ) : (
              <div className="flex gap-2 justify-center md:justify-start">
                <Button 
                  onClick={handleSave} 
                  disabled={updateAvatar.isPending}
                  data-testid="button-save-avatar"
                >
                  {updateAvatar.isPending ? "Saving..." : "Save Avatar"}
                </Button>
                <Button variant="outline" onClick={handleCancel} disabled={updateAvatar.isPending}>
                  Cancel
                </Button>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function BannerUploader({ botProfile }: { botProfile: any }) {
  const [previewUri, setPreviewUri] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const updateBanner = useUpdateBotBanner();

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const dataUri = event.target?.result as string;
      setPreviewUri(dataUri);
    };
    reader.readAsDataURL(file);
  };

  const handleSave = () => {
    if (!previewUri) return;

    updateBanner.mutate({ data: { imageDataUri: previewUri } }, {
      onSuccess: () => {
        toast({
          title: "Banner updated",
          description: "Your bot's banner has been successfully updated.",
        });
        setPreviewUri(null);
        queryClient.invalidateQueries({ queryKey: getGetBotProfileQueryKey() });
      },
      onError: (error: any) => {
        toast({
          title: "Update failed",
          description: error.error || "Banner updates require your bot to be verified or have Nitro. This is a Discord limitation.",
          variant: "destructive",
        });
      }
    });
  };

  const handleCancel = () => {
    setPreviewUri(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const displayUrl = previewUri || botProfile.bannerUrl;
  const bgColor = botProfile.bannerColor || "hsl(var(--primary))";

  return (
    <Card className="border-border/50 shadow-md">
      <CardHeader>
        <CardTitle className="text-xl">Profile Banner</CardTitle>
        <CardDescription>
          Update the banner that appears at the top of your bot's profile.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <Alert variant="default" className="bg-primary/10 border-primary/20 text-primary-foreground">
          <AlertCircle className="h-4 w-4 text-primary" />
          <AlertTitle>Note on Banner Updates</AlertTitle>
          <AlertDescription className="text-primary-foreground/80 text-sm mt-1">
            Banner updates via the API require your bot to be verified or belong to a boosted server. 
            If your bot lacks these privileges, the update will fail. This is a Discord limitation.
          </AlertDescription>
        </Alert>

        <div className="relative rounded-lg overflow-hidden border border-border bg-muted aspect-[3/1] max-w-2xl mx-auto shadow-inner">
          {displayUrl ? (
            <img src={displayUrl} alt="Bot Banner" className="w-full h-full object-cover" data-testid="img-banner-preview" />
          ) : (
            <div 
              className="w-full h-full flex flex-col items-center justify-center" 
              style={{ backgroundColor: bgColor }}
            >
              <ImageIcon className="w-12 h-12 text-white/50 mb-2" />
              <span className="text-white/70 font-medium">No Banner Set</span>
            </div>
          )}
        </div>

        <input 
          type="file" 
          accept="image/*" 
          className="hidden" 
          ref={fileInputRef} 
          onChange={handleFileSelect} 
          data-testid="input-banner-file"
        />

        <div className="flex justify-center md:justify-start">
          {!previewUri ? (
            <Button onClick={() => fileInputRef.current?.click()} data-testid="button-select-banner">
              Change Banner
            </Button>
          ) : (
            <div className="flex gap-2">
              <Button 
                onClick={handleSave} 
                disabled={updateBanner.isPending}
                data-testid="button-save-banner"
              >
                {updateBanner.isPending ? "Saving..." : "Save Banner"}
              </Button>
              <Button variant="outline" onClick={handleCancel} disabled={updateBanner.isPending}>
                Cancel
              </Button>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export default function Home() {
  const { data: botProfile, isLoading, error } = useGetBotProfile();

  // Set dark mode explicitly on document root
  useEffect(() => {
    document.documentElement.classList.add("dark");
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-[100dvh] bg-background text-foreground p-6 md:p-12">
        <div className="max-w-4xl mx-auto space-y-8">
          <div>
            <Skeleton className="h-10 w-64 mb-2" />
            <Skeleton className="h-5 w-96" />
          </div>
          <Skeleton className="h-[250px] w-full rounded-xl" />
          <Skeleton className="h-[400px] w-full rounded-xl" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-[100dvh] bg-background text-foreground flex items-center justify-center p-6">
        <Card className="max-w-md w-full border-destructive/50">
          <CardHeader>
            <CardTitle className="text-destructive flex items-center gap-2">
              <AlertCircle className="h-5 w-5" />
              Error Loading Profile
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">
              {error?.error || "Failed to load bot profile. Please check your configuration and API token."}
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!botProfile) return null;

  return (
    <div className="min-h-[100dvh] bg-background text-foreground p-4 md:p-8 lg:p-12 font-sans selection:bg-primary/30">
      <div className="max-w-4xl mx-auto space-y-8">
        
        <header className="border-b border-border/40 pb-6 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold tracking-tight text-foreground">Bot Customizer</h1>
              <p className="text-muted-foreground mt-2 text-sm md:text-base">
                Manage your Discord bot's identity and appearance. Changes apply immediately.
              </p>
            </div>
            <div className="hidden md:flex items-center gap-3 px-4 py-2 bg-muted rounded-full border border-border/50">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              <span className="text-sm font-medium text-muted-foreground">System Online</span>
            </div>
          </div>
        </header>

        <main className="space-y-8">
          <AvatarUploader botProfile={botProfile} />
          <BannerUploader botProfile={botProfile} />
        </main>
        
        <footer className="pt-12 pb-6 text-center text-sm text-muted-foreground border-t border-border/30">
          <p>Discord Bot Control Panel &bull; Changes are synced via the Discord API.</p>
        </footer>
      </div>
    </div>
  );
}
