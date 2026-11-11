
"use client";

import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
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

export default function Home() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const inputRef = useRef<HTMLInputElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const [playlists, setPlaylists] = useState<Playlist[]>([]);
  const [selectedPlaylist, setSelectedPlaylist] = useState("");
  const [videos, setVideos] = useState<Video[]>([]);
  const [selectedVideo, setSelectedVideo] = useState("");

  useEffect(() => {
  async function fetchPlaylists() {
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/playlists"
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
}, []);

useEffect(() => {
    if (!selectedPlaylist) return;

    async function fetchVideos() {
      try {
        const response = await fetch(
          `http://127.0.0.1:8000/api/playlists/${selectedPlaylist}/videos`
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
  }, [selectedPlaylist]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function handleSubmit(e?: React.FormEvent<HTMLFormElement>, prompt?: string) {
    e?.preventDefault();

    const userQuestion = (prompt || question).trim();

    if (!userQuestion || loading) return;

    setMessages((prev) => [
      ...prev,
      { role: "user", content: userQuestion },
    ]);

    setQuestion("");
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: userQuestion,
          limit: 5,
        }),
      });

      if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
      }

      const data = await response.json();
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

        <div className="hidden items-center gap-2 rounded-full border border-white/[0.07] px-3 py-2 sm:flex">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
          <span className="text-[11px] text-slate-400">
            Learning engine online
          </span>
        </div>
      </header>

      <div className="flex flex-1 flex-col overflow-y-auto">
        <div className="border-b border-white/[0.07] bg-[#101010] px-5 py-4 md:px-8">
          <div className="mx-auto flex max-w-4xl flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="mb-1 text-[10px] font-semibold tracking-[2px] text-amber-400">
                YOUR COURSE
              </p>
              <h3 className="text-sm font-semibold text-white">
                {playlists.find(
                  (p) => p.playlist_id === selectedPlaylist
                )?.playlist_title || "Loading playlist..."}
              </h3>
              <p className="mt-1 text-xs text-slate-500">
                {videos.length} videos available
              </p>
            </div>

            <div className="flex flex-col gap-2 sm:w-72">
              <label className="text-xs text-slate-500">
                Select a video
              </label>
              <select
                value={selectedVideo}
                onChange={(e) => setSelectedVideo(e.target.value)}
                className="w-full rounded-lg border border-white/[0.10] bg-[#171717] px-3 py-2.5 text-sm text-white outline-none focus:border-amber-400/40"
              >
                {videos.map((video) => (
                  <option key={video.video_id} value={video.video_id}>
                    {video.title}
                  </option>
                ))}
              </select>
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
  </main>
);
}
