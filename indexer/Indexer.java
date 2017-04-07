//##############################################
//   FileName:    Indexer.java
//   Author:      Simon Baker
//   Affiliation: University of Cambridge
//                Computer Laboratory and Language Technology Laboratory
//   Contact:     simon.baker.gen@gmail.com
//                simon.baker@cl.cam.ac.uk
//
//   Description: This class represents an indexer where data for the hallmarks classifer is read and indexed in Lucene.  it should be run from main using the runme.sh script.
//                It takes the file that contains all of the pubmed folders that have ben sentence segmented, as as well as a sister directory in ./pub_out/*/ann/ that contains the hallmark annotations.
//                the indexer also takes the output index dir as a paramater, and the number of threads to run in parellel. 
//                The indexer implements consumer-producer design pattern. 


import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.io.PrintWriter;
import java.lang.management.ManagementFactory;
import java.lang.management.RuntimeMXBean;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.Map.Entry;
import java.util.Stack;
import java.util.Vector;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.TimeUnit;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.lucene.analysis.core.SimpleAnalyzer;
import org.apache.lucene.analysis.core.WhitespaceAnalyzer;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.IntField;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.index.IndexWriterConfig.OpenMode;
import org.apache.lucene.queryparser.classic.MultiFieldQueryParser;
import org.apache.lucene.queryparser.classic.ParseException;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.queryparser.ext.Extensions.Pair;
import org.apache.lucene.search.BooleanClause;
import org.apache.lucene.search.BooleanQuery;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopScoreDocCollector;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;
import org.apache.lucene.util.Version;
import org.apache.lucene.util.StringHelper;
import org.jsoup.*;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.nodes.Node;
import org.jsoup.nodes.TextNode;
import org.jsoup.select.Elements;
import org.jsoup.select.NodeVisitor;
import org.omg.CosNaming.NameComponentHolder;


public class Indexer {

	private ProducerConsumer _pc;

	public void Join() {
		_pc.Join();
	}

	public void Init(int N) {
		_pc.Init(N);
	}

	public Indexer() {
		_pc = new ProducerConsumer();
	}

	public void Enqueue(int id, String e, IndexWriter writer) {

		_pc.Enqueue(id, e, writer);

	}

	public static class ProducerConsumer {

		public class Item {

			public int _id;
			public String _dir;
			public IndexWriter _writer;

			public Item(int id, String e, IndexWriter output) {
				_id = id;
				_dir = e;
				_writer = output;
			}
		}

		public void Join() {
			// pool.shutdown();
			// pool.Join();
			pool.shutdown();
			try {
				pool.awaitTermination(Long.MAX_VALUE, TimeUnit.NANOSECONDS);
			} catch (InterruptedException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
			// ----------- Cleanup ------------------

		}

		private ExecutorService pool = null;
		private BlockingQueue<Item> queue = null;

		public ProducerConsumer() {
			queue = new LinkedBlockingQueue<Item>();
		}

		public void Init(int N) {
			pool = Executors.newFixedThreadPool(N);
			for (int i = 0; i < N; i++) {
				pool.execute(new Consumer(i));
			}
		}

		public void Enqueue(int id, String e, IndexWriter output) {
			queue.add(new Item(id, e, output));
		}

		private class Consumer implements Runnable {

			private volatile int _id = -1;
			private volatile int _fresh = 0;

			private int _name_pos = 0;

			private String[] names = null;

			private String Name() {
				if (names != null && _name_pos < names.length) {
					return (names[++_name_pos]);
				}
				return null;
			}

			public Consumer(int id) {
				_id = id;
			}

			@Override
			public void run() {
				IndexWriter output  = null;
				while(!queue.isEmpty()) {
					try {
						Item item = queue.take();
						String directory = item._dir;
						output  = item._writer;
						System.out.println("processing: " + directory);
						String annoDir = item._dir.replace("sent", "pub_out")+File.separator+"ann"+File.separator;
						File folder = new File(directory);
						File[] listOfFiles = folder.listFiles();
						for (int i = 0; i < listOfFiles.length; i++) {
							if (listOfFiles[i].isFile()) 
								String data = readFile(listOfFiles[i].getPath());
								HashMap<String, HallmarkRecord> hallmarksMap = null;
								String[] records = data.split("\n");
								String pubmedID = listOfFiles[i].getName().replaceAll(".txt", "");
								String annotationFilePath = annoDir + pubmedID +".ann";
								hallmarksMap = getHallmarksDict(annotationFilePath);
								for(String rec : records) {								
									String[] fields = rec.split("\t");
									String sentID = fields[0];
									String sentText = fields[1];
									
									org.apache.lucene.document.Document doc = new org.apache.lucene.document.Document();
									doc.add(new Field("id", sentID,Field.Store.YES, Field.Index.NOT_ANALYZED,Field.TermVector.NO));
									doc.add(new Field("text", sentText,Field.Store.YES, Field.Index.ANALYZED,Field.TermVector.WITH_POSITIONS_OFFSETS));
									
									
									String hallmarks="";
									String hallmarks_exp="";
									String pos="";
									if (hallmarksMap != null && hallmarksMap.containsKey(sentID)){
										
										hallmarks = hallmarksMap.get(sentID).hallmarkString;
										hallmarks_exp = hallmarksMap.get(sentID).getExpandedHallmarks();
										pos = hallmarksMap.get(sentID).poistionString;
									}
									
									doc.add(new Field("hallmarks",hallmarks,Field.Store.YES, Field.Index.ANALYZED,Field.TermVector.WITH_POSITIONS_OFFSETS));
									doc.add(new Field("hallmarks-exp",hallmarks_exp,Field.Store.YES, Field.Index.ANALYZED,Field.TermVector.WITH_POSITIONS_OFFSETS));
									doc.add(new Field("pos",pos,Field.Store.YES, Field.Index.NOT_ANALYZED,Field.TermVector.NO));
																		
									output.addDocument(doc);
								}
								
						    } else if (listOfFiles[i].isDirectory()) {
						        System.out.println("Directory " + listOfFiles[i].getName());
						    }
						 }
						
					} catch(Exception e) {
						System.out.println(e.getMessage());
						e.printStackTrace();
					}
					System.out.print("...done\n");
				}
				
			}

			private HashMap<String, HallmarkRecord> getHallmarksDict(String annotationFilePath) {
				
				File annoFile = new File(annotationFilePath);
				if (!annoFile.exists()) return null;

				String data = readFile(annotationFilePath);
				HashMap<String, HallmarkRecord> returnMap = new HashMap<String, HallmarkRecord>();
				String[] recs = data.split("\n");
				//System.out.println("anno file: " + annotationFilePath);
				for (String rec : recs) {
					String[] fields = rec.split("\t");
					HallmarkRecord hmr = new HallmarkRecord(fields[0], fields[1], fields[2]);
					returnMap.put(hmr.sentID, hmr);
				}
				return returnMap;

			}
		}

	}

	public static String readFile(String file) {
	
		BufferedReader br= null;
		try{
			br = new BufferedReader(new FileReader(file));	
			StringBuilder sb = new StringBuilder();
			String line = br.readLine();

			while (line != null) {
				sb.append(line);
				sb.append("\n");
				line = br.readLine();
			}
			String everything = sb.toString();
			br.close();
			return everything;
		} catch (IOException e) {
			throw new RuntimeException(e);
			
		} finally {
			try {
				br.close();
			} catch (IOException e) {
				throw new RuntimeException(e);
			}
		}

	}


	public static void main(String[] args) {
		// Inputs
		// 1. Path to metadata
		// 2. Path to Interim folder
		// 3. Path to type index
		// 4. Output index

		// GEt command-line arguments
		/*
		 RuntimeMXBean RuntimemxBean = ManagementFactory.getRuntimeMXBean(); 
		 List<String> paramList=new ArrayList<String>(); 
		 paramList.addAll(RuntimemxBean.getInputArguments() ); 
		 paramList.add(RuntimemxBean.getClassPath() ); 
		 paramList.add(RuntimemxBean.getBootClassPath() ); 
		 paramList.add(RuntimemxBean.getLibraryPath() );
		 
		 for( String p : paramList ) { System.out.println( p ); }
		 
		 System.exit(1);
		*/
		if (args.length < 2) {
			System.out.println("Usage: Indexer <dirFile> <output_index> <number of threads>");
			System.exit(1);
		}
		String DIRFILE = args[0];
		String OUTPUT = args[1];
		int NUM_THR = Integer.parseInt(args[2]);

		// open output index for writing
		Directory INDEX_WDIR = null;
		try {
			INDEX_WDIR = FSDirectory.open(new File(OUTPUT));
		} catch (IOException ioe) {
			System.out.println("Could not open one of the necessary directories");
			System.exit(1);
		}

		IndexWriterConfig iwc = new IndexWriterConfig(Version.LUCENE_CURRENT,
				new StandardAnalyzer(Version.LUCENE_CURRENT));
		iwc.setOpenMode(OpenMode.CREATE);
		IndexWriter writer = null;

		try {
			writer = new IndexWriter(INDEX_WDIR, iwc);
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			System.out.println("Could not open output index for writing");
			System.exit(1);
		}

		int i = 0;
		Indexer swv = new Indexer();
		String temp = readFile(DIRFILE);
		String[] dirs = temp.split("\n");
		for (String dir : dirs) {
			swv.Enqueue(i, dir, writer);
			i++;
		}
		swv.Init(NUM_THR);
		swv.Join();
		try {
			writer.close();
		} catch (IOException e1) {
			e1.printStackTrace();
		}

	}

}
