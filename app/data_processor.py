import os
from pymongo import MongoClient
from neo4j import GraphDatabase

class KnowledgeGraphBuilder:
  def __init__(self):
    # Connect to MongoDB
    self.mongo_uri = os.getenv("MONGODB_URI")
    self.mongo_client = MongoClient(self.mongo_uri)
    self.mongo_db = self.mongo_client["Github-Webhook"]
    self.mongo_collection = self.mongo_db["github_events"]

    # Connect to Neo4j
    self.neo4j_uri = os.getenv("NEO4J_URI")
    self.neo4j_username = os.getenv("NEO4J_USERNAME")
    self.neo4j_password = os.getenv("NEO4J_PASSWORD")
    self.neo4j_driver = GraphDatabase.driver(
      self.neo4j_uri, auth=(self.neo4j_username, self.neo4j_password)
    )

  def close_connections(self):
    """Close connections to MongoDB and Neo4j."""
    self.mongo_client.close()
    self.neo4j_driver.close()

  def process_commits(self):
    """Process commit data from MongoDB and build the Knowledge Graph."""
    try:
      # Fetch data from MongoDB
      events = self.mongo_collection.find({"commits": {"$exists": True}})
      print(f"Found {self.mongo_collection.count_documents({'commits': {'$exists': True}})} records with commits in MongoDB.")

      with self.neo4j_driver.session() as session:
        for event in events:
          self.create_graph_from_commit_event(session, event)

    except Exception as e:
      print(f"Error processing data: {e}")
    finally:
      self.close_connections()

  def create_graph_from_commit_event(self, session, event):
    """Create nodes and relationships from commit event data."""
    # Extract Repository Info
    repository = event["repository"]["name"]
    full_name = event["repository"]["full_name"]
    private = event["repository"]["private"]
    fork = event["repository"]["fork"]
    description = event["repository"].get("description", "No description")
    repo_owner = event["repository"]["owner"]["login"]

    # Extract User Info
    pusher_name = event["pusher"]["name"]
    pusher_email = event["pusher"].get("email", "No email provided")
    pusher_url = event["repository"]["owner"]["html_url"]

    # Extract Commit Info
    commits = event["commits"]
    ref = event.get("ref", "refs/heads/main")
    before = event["before"]
    after = event["after"]
    created = event.get("created", False)
    deleted = event.get("deleted", False)
    forced = event.get("forced", False)
    compare = event.get("compare", "")

    # Create Repository node
    session.run(
      """
      MERGE (r:Repository {name: $repository})
      SET r.full_name = $full_name,
          r.private = $private,
          r.fork = $fork,
          r.description = $description,
          r.owner = $repo_owner
      """,
      repository=repository,
      full_name=full_name,
      private=private,
      fork=fork,
      description=description,
      repo_owner=repo_owner
    )

    # Create User node
    session.run(
      """
      MERGE (u:User {name: $pusher_name})
      SET u.html_url = $pusher_url, u.email = $pusher_email
      """,
      pusher_name=pusher_name,
      pusher_url=pusher_url,
      pusher_email=pusher_email
    )

    # Process each commit
    for commit in commits:
      commit_id = commit["id"]
      message = commit["message"]
      timestamp = commit["timestamp"]
      url = commit["url"]
      added = commit.get("added", [])
      removed = commit.get("removed", [])
      modified = commit.get("modified", [])

      # Create Commit node
      session.run(
        """
        MERGE (c:Commit {id: $commit_id})
        SET c.ref = $ref,
            c.before = $before,
            c.after = $after,
            c.created = $created,
            c.deleted = $deleted,
            c.forced = $forced,
            c.compare = $compare,
            c.message = $message,
            c.timestamp = $timestamp,
            c.url = $url
        """,
        commit_id=commit_id,
        ref=ref,
        before=before,
        after=after,
        created=created,
        deleted=deleted,
        forced=forced,
        compare=compare,
        message=message,
        timestamp=timestamp,
        url=url
      )

      # Create MADE relationship
      session.run(
        """
        MATCH (u:User {name: $pusher_name}), (c:Commit {id: $commit_id})
        MERGE (u)-[:MADE]->(c)
        """,
        pusher_name=pusher_name,
        commit_id=commit_id
      )

      # Create PUSHED relationship
      session.run(
        """
        MATCH (c:Commit {id: $commit_id}), (r:Repository {name: $repository})
        MERGE (c)-[:PUSHED]->(r)
        """,
        commit_id=commit_id,
        repository=repository
      )

      # Create PREVIOUS relationship if applicable
      if before != "0000000000000000000000000000000000000000":
        session.run(
          """
          MATCH (prev:Commit {id: $before}), (curr:Commit {id: $commit_id})
          MERGE (curr)-[:PREVIOUS]->(prev)
          """,
          before=before,
          commit_id=commit_id
        )

      # Process files added, removed, modified
      for file in added:
        session.run(
          """
          MERGE (f:File {name: $file})
          MERGE (c:Commit {id: $commit_id})
          MERGE (c)-[:ADDED]->(f)
          """,
          file=file,
          commit_id=commit_id
        )
      for file in removed:
        session.run(
          """
          MERGE (f:File {name: $file})
          MERGE (c:Commit {id: $commit_id})
          MERGE (c)-[:REMOVED]->(f)
          """,
          file=file,
          commit_id=commit_id
        )
      for file in modified:
        session.run(
          """
          MERGE (f:File {name: $file})
          MERGE (c:Commit {id: $commit_id})
          MERGE (c)-[:MODIFIED]->(f)
          """,
          file=file,
          commit_id=commit_id
        )
