import { useState, useEffect } from "react";

const BASE_URL = "https://jdashboard.tuschkoreit.de/tasks";

interface Tasks {
  id: number;
  title: string;
}

export default function Tasklist() {


  useEffect(() => {
    const fetchPosts = async () => {
      abortControllerRef.current?.abort();
      abortControllerRef.current = new AbortController();

      setIsLoading(true);
    };

    fetchPosts();
  }, [page]);



  return (
    <div className="tutorial">
      <h1 className="mb-4 text-2xl">Data Fething in React</h1>
      <button onClick={() => setPage(page + 1)}>Increase Page ({page})</button>
      {isLoading && <div>Loading...</div>}
      {!isLoading && (
        <ul>
          {posts.map((post) => {
            return <li key={post.id}>{post.title}</li>;
          })}
        </ul>
      )}
    </div>
  );
}

