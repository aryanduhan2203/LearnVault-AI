
"use client";

import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import AuthScreen from "./components/AuthScreen";
import { supabase } from "../lib/supabase";
import {
  BookOpen,
  BrainCircuit,
  LayoutDashboard,
  Library,
  History,
  Settings,
  Plus,
  Search,
  Send,
  Sparkles,
  PanelLeftClose,
  PlayCircle,
  ExternalLink,
  MessageSquare,
  Clock3,
  GraduationCap,
} from "lucide-react";

interface Playlist {
  playlist_id: string;
  playlist_title: string;
  total_videos: number;
}

interface Video {
  video_id: string;
  title: string;
  url: string;
}

interface Source {
  video_id: string;
  chunk_id: number;
  start_time: number;
  end_time: number;
  score: number;
}

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
}

interface ImportStatus {
  playlist_id: string;
  status: string;
  message: string;
  total_videos?: number;
  processed_videos?: number;
  total_chunks?: number;
  total_embeddings?: number;
  indexed_chunks?: number;
  failed_video_count?: number;
}

export default function Home() {
  const [question, setQuestion] = useState("");
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authLoading, setAuthLoading] = useState(true);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [conversations, setConversations] = useState<{ id: string; title: string }[]>([]);
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const inputRef = useRef<HTMLInputElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const [playlists, setPlaylists] = useState<Playlist[]>([]);
  const [selectedPlaylist, setSelectedPlaylist] = useState("");
  const [videos, setVideos] = useState<Video[]>([]);
  const [selectedVideo, setSelectedVideo] = useState("");
  const [showImportModal, setShowImportModal] = useState(false);
  const [playlistUrl, setPlaylistUrl] = useState("");
  const [importStatus, setImportStatus] = useState<ImportStatus | null>(null);
  const [importing, setImporting] = useState(false);
  const [importError, setImportError] = useState("");

  async function getAuthHeaders() {
    const { data } = await supabase.auth.getSession();

    if (!data.session) {
      throw new Error("Session expired. Please log in again.");
    }

    return {
      Authorization: `Bearer ${data.session.access_token}`,
    };
  }
  async function refreshPlaylists(preferredPlaylistId?: string) {
  const response = await fetch("http://127.0.0.1:8000/api/playlists", {
  headers: await getAuthHeaders(),
});

  if (!response.ok) {
    throw new Error("Failed to refresh playlists");
  }

  const data: Playlist[] = await response.json();
  setPlaylists(data);

  if (preferredPlaylistId && data.some(
    (p) => p.playlist_id === preferredPlaylistId
  )) {
    setSelectedPlaylist(preferredPlaylistId);
  } else if (!selectedPlaylist && data.length > 0) {
    setSelectedPlaylist(data[0].playlist_id);
  }
}
async function fetchConversations(playlistId: string) {
  try {
    const { data: playlistRecord, error: playlistError } =
      await supabase
        .from("playlists")
        .select("id")
        .eq("youtube_playlist_id", playlistId)
        .single();

    if (playlistError) throw playlistError;

    const { data, error } = await supabase
      .from("conversations")
      .select("id, title")
      .eq("playlist_id", playlistRecord.id)
      .order("created_at", { ascending: false });

    if (error) throw error;

    setConversations(data || []);
  } catch (error) {
    console.error("Conversation fetch error:", error);
  }
}

async function loadConversation(id: string) {
  try {
    const { data, error } = await supabase
      .from("messages")
      .select("role, content, sources")
      .eq("conversation_id", id)
      .order("created_at", { ascending: true });

    if (error) throw error;

    setConversationId(id);

    setMessages(
      (data || []).map((message) => ({
        role: message.role as "user" | "assistant",
        content: message.content,
        sources: message.sources || [],
      }))
    );
  } catch (error) {
    console.error("Message loading error:", error);
  }
}

  async function handleImportPlaylist(
      e: React.FormEvent<HTMLFormElement>
    ) {
      e.preventDefault();

      if (!playlistUrl.trim() || importing) return;

      setImporting(true);
      setImportError("");
      setImportStatus(null);

      try {
        const authHeaders = await getAuthHeaders();

        const response = await fetch(
          "http://127.0.0.1:8000/api/playlists/import",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              ...authHeaders,
            },
            body: JSON.stringify({
              playlist_url: playlistUrl.trim(),
            }),
          }
        );

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || "Playlist import failed");
        }

        setImportStatus(data);

        if (data.status === "already_imported") {
          await refreshPlaylists(data.playlist_id);
          setImporting(false);
          return;
        }

        while (true) {
          await new Promise((resolve) => setTimeout(resolve, 2000));

          const statusResponse = await fetch(
            `http://127.0.0.1:8000/api/playlists/${data.playlist_id}/status`,
            {
              headers: await getAuthHeaders(),
            }
          );

          if (!statusResponse.ok) {
            throw new Error("Failed to check import status");
          }

          const statusData: ImportStatus = await statusResponse.json();
          setImportStatus(statusData);

          if (statusData.status === "ready") {
            await refreshPlaylists(data.playlist_id);
            break;
          }

          if (
            statusData.status === "failed" ||
            statusData.status === "not_found"
          ) {
            break;
          }
        }
      } catch (error) {
        setImportError(
          error instanceof Error ? error.message : "Something went wrong"
        );
      } finally {
        setImporting(false);
      }
    }
useEffect(() => {
  async function checkSession() {
    const { data } = await supabase.auth.getSession();
    setIsAuthenticated(!!data.session);
    setAuthLoading(false);
  }

  checkSession();

  const { data: listener } = supabase.auth.onAuthStateChange(
    (_event, session) => {
      setIsAuthenticated(!!session);
    }
  );

  return () => {
    listener.subscription.unsubscribe();
  };
}, []);
  useEffect(() => {
  if (!isAuthenticated) return;

  async function fetchPlaylists() {
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/playlists",
        {
          headers: await getAuthHeaders(),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to fetch playlists");
      }

      const data: Playlist[] = await response.json();

      setPlaylists(data);

      if (data.length > 0) {
        setSelectedPlaylist(data[0].playlist_id);
      }
    } catch (error) {
      console.error("Playlist fetch error:", error);
    }
  }

  fetchPlaylists();
}, [isAuthenticated]);

useEffect(() => {
    if (!isAuthenticated || !selectedPlaylist) return;

    async function fetchVideos() {
      try {
        const response = await fetch(
          `http://127.0.0.1:8000/api/playlists/${selectedPlaylist}/videos`,
          {
            headers: await getAuthHeaders(),
          }
        );
        if (!response.ok) {
          throw new Error("Failed to fetch videos");
        }

        const data = await response.json();

        console.log("Videos API response:", data);

        setVideos(data.videos);

        if (data.videos.length > 0) {
          setSelectedVideo(data.videos[0].video_id);
        } else {
          setSelectedVideo("");
        }
     } catch (error) {
       console.error("Video fetch error:", error);
       setVideos([]);
       setSelectedVideo("");
      }
    }

  fetchVideos();
  }, [selectedPlaylist,isAuthenticated]);
  useEffect(() => {
    if (!isAuthenticated || !selectedPlaylist) return;

    fetchConversations(selectedPlaylist);
  }, [selectedPlaylist, isAuthenticated]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  
  async function handleSubmit(
    e?: React.FormEvent<HTMLFormElement>,
    prompt?: string
  ) {
    e?.preventDefault();

    const userQuestion = (prompt || question).trim();

    if (!userQuestion || loading || !selectedPlaylist) return;

    setMessages((prev) => [
      ...prev,
      { role: "user", content: userQuestion },
    ]);

    setQuestion("");
    setLoading(true);

    try {
      let activeConversationId = conversationId;

      if (!activeConversationId) {
        const { data: sessionData } = await supabase.auth.getSession();

        if (!sessionData.session) {
          throw new Error("Session expired. Please log in again.");
        }

        const { data: playlistRecord, error: playlistError } =
          await supabase
            .from("playlists")
            .select("id")
            .eq("youtube_playlist_id", selectedPlaylist)
            .single();

        if (playlistError) {
          throw playlistError;
        }

        const { data: conversation, error: conversationError } =
          await supabase
            .from("conversations")
            .insert({
              user_id: sessionData.session.user.id,
              playlist_id: playlistRecord.id,
              title: userQuestion.slice(0, 60),
            })
            .select("id")
            .single();

        if (conversationError) {
          throw conversationError;
        }

        activeConversationId = conversation.id;
        setConversationId(activeConversationId);
        await fetchConversations(selectedPlaylist);
      }
      const { error: userMessageError } = await supabase
        .from("messages")
        .insert({
          conversation_id: activeConversationId,
          role: "user",
          content: userQuestion,
        });

      if (userMessageError) {
        throw userMessageError;
      }

      const response = await fetch("http://127.0.0.1:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(await getAuthHeaders()),
        },
        body: JSON.stringify({
          question: userQuestion,
          playlist_id: selectedPlaylist,
          limit: 5,
        }),
      });

      if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
      }

      const data = await response.json();

      const { error: assistantMessageError } = await supabase
        .from("messages")
        .insert({
          conversation_id: activeConversationId,
          role: "assistant",
          content: data.answer,
          sources: data.sources || [],
        });

      if (assistantMessageError) {
        throw assistantMessageError;
      }
      console.log("Videos API response:", data);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources || [],
        },
      ]);
    } catch (error) {
      console.error(error);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "I couldn't connect to the learning engine. Please check that your backend is running and try again.",
        },
      ]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }


  function formatTime(seconds: number) {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);

  return `${minutes}:${String(remainingSeconds).padStart(2, "0")}`;
  }

  if (authLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#090909] text-amber-400">
        Loading LearnVault...
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <AuthScreen
        onAuthSuccess={() => setIsAuthenticated(true)}
      />
    );
  }

  return (
    <main className="flex h-screen overflow-hidden bg-[#090909] text-slate-200">
    {sidebarOpen && (
      <aside className="hidden w-[250px] shrink-0 flex-col border-r border-white/[0.07] bg-[#101010] md:flex">
        <div className="flex h-[76px] items-center gap-3 border-b border-white/[0.07] px-6">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-amber-500/15 text-amber-400">
            <BrainCircuit size={21} />
          </div>
          <div>
            <h1 className="text-[16px] font-bold tracking-tight text-white">
              LearnVault
            </h1>
            <p className="text-[10px] tracking-[2px] text-slate-500">
              AI LEARNING SPACE
            </p>
          </div>
        </div>

        <div className="p-4">
          <button className="flex w-full items-center gap-2 rounded-lg bg-amber-400 px-4 py-3 text-sm font-semibold text-black transition hover:bg-amber-300">
            <Plus size={17} />
            New conversation
          </button>
        </div>

        <div className="space-y-1 px-3">
          <p className="mb-3 px-3 text-[10px] font-semibold tracking-[2px] text-slate-600">
            WORKSPACE
          </p>

          {[
            { icon: LayoutDashboard, label: "Dashboard" },
            { icon: MessageSquare, label: "AI Tutor", active: true },
            { icon: Library, label: "My Courses" },
            { icon: BookOpen, label: "Revision Notes" },
            { icon: History, label: "History" },
          ].map((item) => (
            <button
              key={item.label}
              className={`flex w-full items-center gap-3 rounded-lg px-3 py-3 text-sm transition ${
                item.active
                  ? "bg-amber-500/10 font-medium text-amber-300"
                  : "text-slate-400 hover:bg-white/[0.04] hover:text-white"
              }`}
            >
              <item.icon size={17} />
              {item.label}
            </button>
          ))}
        </div>

        <div className="mx-5 my-6 border-t border-white/[0.07]" />

        <div className="px-6">
          <p className="mb-4 text-[10px] font-semibold tracking-[2px] text-slate-600">
            YOUR LEARNING SPACE
          </p>

          <div className="rounded-xl border border-white/[0.07] bg-white/[0.025] p-3">
            <div className="mb-2 flex items-center gap-2">
              <GraduationCap size={16} className="text-amber-400" />
              <span className="text-xs font-semibold text-slate-200">
                Active knowledge base
              </span>
            </div>
            <p className="text-xs leading-5 text-slate-500">
              Backend from first principles
            </p>
            <div className="mt-3 flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
              <span className="text-[10px] text-emerald-400">
                Knowledge base connected
              </span>
            </div>
          </div>
        </div>
        <div className="px-5 mt-6">
        <p className="mb-3 text-[10px] font-semibold tracking-[2px] text-slate-600">
                      YOUR CONVERSATIONS
                    </p>

                    <div className="max-h-48 space-y-1 overflow-y-auto">
                      {conversations.map((conversation) => (
                        <button
                          key={conversation.id}
                          onClick={() => loadConversation(conversation.id)}
                          className="w-full truncate rounded-lg px-3 py-2 text-left text-xs text-slate-400 transition hover:bg-white/[0.05] hover:text-white"
                        >
                          <MessageSquare size={13} className="mr-2 inline" />
                          {conversation.title}
                        </button>
                      ))}

                      {conversations.length === 0 && (
                        <p className="px-3 text-xs text-slate-600">
                          No conversations yet
                        </p>
                      )}
                    </div>
                  </div>
        <div className="mt-auto border-t border-white/[0.07] p-4">
          <button className="flex w-full items-center gap-3 rounded-lg p-2 text-sm text-slate-400 hover:bg-white/[0.04]">
            <Settings size={17} />
            Settings
          </button>
          <div className="mt-3 flex items-center gap-3 rounded-lg bg-white/[0.03] p-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-amber-500/20 text-sm font-bold text-amber-300">
              A
            </div>
            <div>
              <p className="text-xs font-semibold text-white">My Workspace</p>
              <p className="text-[10px] text-slate-500">Personal account</p>
            </div>
          </div>
        </div>
      </aside>
    )}

    <section className="flex min-w-0 flex-1 flex-col">
      <header className="flex h-[76px] shrink-0 items-center justify-between border-b border-white/[0.07] px-5 md:px-8">
        <div className="flex items-center gap-4">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="rounded-lg p-2 text-slate-400 hover:bg-white/[0.06]"
            aria-label="Toggle sidebar"
          >
            <PanelLeftClose size={19} />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-semibold text-white">AI Tutor</h2>
              <span className="rounded-md border border-amber-400/20 bg-amber-400/10 px-2 py-0.5 text-[10px] text-amber-300">
                RAG POWERED
              </span>
            </div>
            <p className="mt-1 text-[11px] text-slate-500">
              Ask questions from your learning material
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
        <div className="hidden items-center gap-2 rounded-full border border-white/[0.07] px-3 py-2 sm:flex">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
          <span className="text-[11px] text-slate-400">
            Learning engine online
          </span>
        </div>

        <button
          onClick={async () => {
            const { error } = await supabase.auth.signOut();

            if (error) {
              console.error("Logout failed:", error);
              return;
            }

            setMessages([]);
            setConversationId(null);
            setPlaylists([]);
            setSelectedPlaylist("");
          }}
          className="rounded-lg border border-white/10 px-3 py-2 text-xs text-slate-400 hover:bg-white/5 hover:text-white"
        >
          Log out
        </button>
      </div>
      </header>

      <div className="flex flex-1 flex-col overflow-y-auto">
        
        <div className="border-b border-white/[0.07] bg-[#101010] px-5 py-4 md:px-8">
          <div className="mx-auto flex max-w-4xl flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="mb-1 text-[10px] font-semibold tracking-[2px] text-amber-400">
                YOUR LEARNING SPACE
              </p>
              <h3 className="text-sm font-semibold text-white">
                Choose your learning material
              </h3>
              <p className="mt-1 text-xs text-slate-500">
                {playlists.length} playlists available
              </p>
            </div>

            <div className="flex flex-col gap-2 sm:w-80">
              <label className="text-xs text-slate-500">
                Select a playlist
              </label>

              <select
                value={selectedPlaylist}
                onChange={(e) => {
                  setSelectedPlaylist(e.target.value);
                  setMessages([]);
                  setConversationId(null);
                }}
                className="w-full rounded-lg border border-white/[0.10] bg-[#171717] px-3 py-2.5 text-sm text-white outline-none focus:border-amber-400/40"
              >
                {playlists.map((playlist) => (
                  <option
                    key={playlist.playlist_id}
                    value={playlist.playlist_id}
                  >
                    {playlist.playlist_title}
                  </option>
                ))}
              </select>

              <button
                onClick={() => {
                  setShowImportModal(true);
                  setImportError("");
                  setImportStatus(null);
                }}
                className="flex items-center justify-center gap-2 rounded-lg border border-amber-400/30 bg-amber-500/10 px-3 py-2.5 text-sm font-medium text-amber-300 transition hover:bg-amber-500/20"
              >
                <Plus size={16} />
                Add New Playlist
              </button>
            </div>
          </div>
        </div>


        <div className="mx-auto w-full max-w-4xl flex-1 px-5 py-8 md:px-10">
          {messages.length === 0 ? (
            <div className="flex min-h-[65vh] flex-col items-center justify-center text-center">
              <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl border border-amber-400/20 bg-amber-500/10 text-amber-300 shadow-lg shadow-amber-500/5">
                <Sparkles size={30} />
              </div>

              <p className="mb-3 text-[11px] font-semibold tracking-[3px] text-amber-400">
                YOUR PERSONAL AI TUTOR
              </p>

              <h2 className="max-w-xl text-3xl font-semibold tracking-tight text-white md:text-4xl">
                What would you like to
                <span className="text-amber-400"> learn today?</span>
              </h2>

              <p className="mt-4 max-w-lg text-sm leading-7 text-slate-500">
                Ask anything about your course videos. LearnVault retrieves
                relevant transcript passages and uses them to generate
                grounded answers.
              </p>

              <div className="mt-10 grid w-full max-w-2xl gap-3 sm:grid-cols-2">
                {[
                  "What is database indexing?",
                  "Explain load balancing",
                  "SQL vs NoSQL databases",
                  "How does a backend server work?",
                ].map((prompt) => (
                  <button
                    key={prompt}
                    onClick={() => handleSubmit(undefined, prompt)}
                    className="group flex items-center justify-between rounded-xl border border-white/[0.08] bg-white/[0.025] p-4 text-left text-sm text-slate-400 transition hover:border-amber-400/30 hover:bg-amber-500/[0.06] hover:text-white"
                  >
                    {prompt}
                    <span className="text-amber-400 opacity-0 transition group-hover:opacity-100">
                      <Send size={15} />
                    </span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-8 pb-10">
              {messages.map((message, index) => (
                <div key={index}>
                  {message.role === "user" ? (
                    <div className="flex justify-end">
                      <div className="max-w-[85%] rounded-2xl rounded-br-sm bg-amber-500/15 px-5 py-4 text-sm leading-7 text-amber-100">
                        {message.content}
                      </div>
                    </div>
                  ) : (
                    <div className="flex gap-4">
                      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-amber-400/20 bg-amber-500/10 text-amber-300">
                        <BrainCircuit size={19} />
                      </div>

                      <div className="min-w-0 flex-1">
                        <div className="mb-3 flex items-center gap-2">
                          <span className="text-sm font-semibold text-white">
                            LearnVault AI
                          </span>
                          <span className="text-[10px] text-emerald-400">
                            GROUNDED RESPONSE
                          </span>
                        </div>

                        <div className="prose prose-invert max-w-none text-sm leading-7 text-slate-300 prose-headings:text-white prose-strong:text-white prose-a:text-amber-300">
                          <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {message.content}
                          </ReactMarkdown>
                        </div>

                        
                        {message.sources && message.sources.length > 0 && (
                          <div className="mt-7 border-t border-white/[0.07] pt-5">
                            {(() => {
                              const bestSource = [...message.sources].sort(
                                (a, b) => b.score - a.score
                              )[0];

                              return (
                                <div>
                                  <div className="mb-3">
                                    <h3 className="text-sm font-semibold text-white">
                                      Recommended lecture
                                    </h3>
                                    <p className="mt-1 text-xs text-slate-500">
                                      Relevant explanation from your course
                                    </p>
                                  </div>

                                  <div className="w-full max-w-2xl overflow-hidden rounded-xl border border-white/[0.08] bg-black">
                                    <div className="aspect-video">
                                      <iframe
                                        key={`${bestSource.video_id}-${bestSource.start_time}`}
                                        src={`https://www.youtube.com/embed/${bestSource.video_id}?start=${Math.floor(bestSource.start_time)}&autoplay=0`}
                                        title="Relevant course explanation"
                                        className="h-full w-full"
                                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                                        allowFullScreen
                                      />
                                    </div>
                                  </div>

                                  <div className="mt-3 flex items-center gap-2 text-xs text-amber-300">
                                    <Clock3 size={13} />
                                    Starts at {formatTime(bestSource.start_time)}
                                  </div>
                                </div>
                              );
                            })()}
                          </div>
                        )}

                      </div>
                    </div>
                  )}
                </div>
              ))}

              {loading && (
                <div className="flex items-center gap-3 text-sm text-amber-300">
                  <div className="flex gap-1">
                    <span className="h-2 w-2 animate-bounce rounded-full bg-amber-400" />
                    <span className="h-2 w-2 animate-bounce rounded-full bg-amber-400 [animation-delay:150ms]" />
                    <span className="h-2 w-2 animate-bounce rounded-full bg-amber-400 [animation-delay:300ms]" />
                  </div>
                  Searching your knowledge base...
                </div>
              )}
              <div ref={bottomRef} />
            </div>
          )}
        </div>

        <div className="sticky bottom-0 border-t border-white/[0.07] bg-[#090909]/95 px-5 py-5 backdrop-blur-xl md:px-10">
          <form
            onSubmit={handleSubmit}
            className="mx-auto max-w-4xl"
          >
            <div className="flex items-center gap-3 rounded-2xl border border-white/[0.10] bg-[#171717] p-2 transition focus-within:border-amber-400/40">
              <Search size={18} className="ml-3 shrink-0 text-slate-500" />

              <input
                ref={inputRef}
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask anything about your course..."
                className="min-w-0 flex-1 bg-transparent py-3 text-sm text-white outline-none placeholder:text-slate-600"
                disabled={loading}
              />

              <button
                type="submit"
                disabled={loading || !question.trim()}
                className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-amber-400 text-black transition hover:bg-amber-300 disabled:cursor-not-allowed disabled:opacity-40"
                aria-label="Send message"
              >
                <Send size={17} />
              </button>
            </div>

            <p className="mt-3 text-center text-[10px] text-slate-600">
              LearnVault AI answers using your course transcripts. Always
              verify important information with the original material.
            </p>
          </form>
        </div>
      </div>
    
    </section>

    {showImportModal && (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 px-4 backdrop-blur-sm">
        <div className="w-full max-w-md rounded-2xl border border-white/10 bg-[#141414] p-6 shadow-2xl">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-white">
                Add New Playlist
              </h2>
              <p className="mt-1 text-xs text-slate-500">
                Import your YouTube learning material
              </p>
            </div>

            <button
              onClick={() => {
                if (!importing) {
                  setShowImportModal(false);
                }
              }}
              disabled={importing}
              className="rounded-lg p-2 text-slate-400 hover:bg-white/5 hover:text-white disabled:opacity-40"
              aria-label="Close modal"
            >
              ✕
            </button>
          </div>

          <form onSubmit={handleImportPlaylist}>
            <label className="mb-2 block text-xs font-medium text-slate-400">
              YouTube Playlist URL
            </label>

            <input
              type="url"
              value={playlistUrl}
              onChange={(e) => setPlaylistUrl(e.target.value)}
              placeholder="https://www.youtube.com/playlist?list=..."
              disabled={importing}
              required
              className="w-full rounded-lg border border-white/10 bg-[#090909] px-4 py-3 text-sm text-white outline-none placeholder:text-slate-600 focus:border-amber-400/50 disabled:opacity-50"
            />

            <p className="mt-2 text-[11px] leading-5 text-slate-500">
              Paste a public YouTube playlist link. LearnVault will extract
              transcripts and prepare the content for AI-powered learning.
            </p>

            {importError && (
              <div className="mt-4 rounded-lg border border-red-500/20 bg-red-500/10 p-3 text-xs text-red-400">
                {importError}
              </div>
            )}

            {importStatus && (
              <div className="mt-4 rounded-lg border border-amber-400/20 bg-amber-400/5 p-4">
                <div className="mb-2 flex items-center justify-between">
                  <span className="text-xs font-semibold text-amber-300">
                    {importStatus.status === "ready"
                      ? "Import complete"
                      : importStatus.status === "failed"
                      ? "Import failed"
                      : "Import progress"}
                  </span>
                  <span className="text-[10px] text-slate-400">
                    {importStatus.status}
                  </span>
                </div>

                <p className="text-xs text-slate-400">
                  {importStatus.message}
                </p>

                {importStatus.total_videos !== undefined && (
                  <p className="mt-2 text-xs text-slate-500">
                    Videos: {importStatus.processed_videos || 0} / {importStatus.total_videos}
                  </p>
                )}

                {importStatus.total_chunks !== undefined && (
                  <p className="mt-1 text-xs text-slate-500">
                    Chunks created: {importStatus.total_chunks}
                  </p>
                )}

                {importStatus.indexed_chunks !== undefined && (
                  <p className="mt-1 text-xs text-slate-500">
                    Chunks indexed: {importStatus.indexed_chunks}
                  </p>
                )}
              </div>
            )}

            <div className="mt-6 flex gap-3">
              <button
                type="button"
                onClick={() => setShowImportModal(false)}
                disabled={importing}
                className="flex-1 rounded-lg border border-white/10 px-4 py-3 text-sm text-slate-400 transition hover:bg-white/5 disabled:opacity-40"
              >
                Close
              </button>

              <button
                type="submit"
                disabled={importing || !playlistUrl.trim()}
                className="flex-1 rounded-lg bg-amber-400 px-4 py-3 text-sm font-semibold text-black transition hover:bg-amber-300 disabled:cursor-not-allowed disabled:opacity-40"
              >
                {importing ? "Importing..." : "Import Playlist"}
              </button>
            </div>
          </form>
        </div>
      </div>
    )}
  </main>
);

}
