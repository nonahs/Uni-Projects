package Part1;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.nio.file.Paths;
import java.util.Formatter;
import java.util.Scanner;
import java.util.ArrayList;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.Arrays;

public class Simulation {
	
	private static Scanner input;
	private static String suspectsFile = "suspects.csv";
	private static String policeFile = "police.csv";
	private static String suspectsOutFile = "suspects-output.csv";
	private static String policeOutFile = "police-output.csv";

	public static void main(String[] args) {
				
		openFile(suspectsFile);
		input.nextLine(); // Skip first line
		ArrayList<Suspects> suspectsList = readSuspects();
		input.close();
		
		openFile(policeFile);
		input.nextLine(); // Skip first line
		ArrayList<Police> policeList = readPolice(suspectsList);
		input.close();
		
		int dogs = (int) (Math.ceil(suspectsList.size() / 2d));
		Kennel k1 = new Kennel(dogs);
		
		int unitsPerStation = (int) (Math.ceil(policeList.size() / 4d));
		PoliceStation s1 = new PoliceStation("Downtown", 25, 5, unitsPerStation);
		PoliceStation s2 = new PoliceStation("Midtown", 80, 30, unitsPerStation);
		PoliceStation s3 = new PoliceStation("Uptown", 10, 90, unitsPerStation);
		PoliceStation s4 = new PoliceStation("LazyTown", 70, 80, unitsPerStation);
		ArrayList<PoliceStation> stationList = new ArrayList<PoliceStation>();
		stationList.addAll(Arrays.asList(s1, s2, s3, s4));

		for (Police p : policeList) { //pass all kennel/station objects to all police
			p.setKennel(k1);
			p.setStations(stationList);
		}
		
		ExecutorService executorService = Executors.newCachedThreadPool();
		
		int currentCycle = 0;
		long lastCycleTime = 0;
		int maxCycles = 60;
		
		System.out.println("Executing Simulation...");
		
		while(currentCycle<maxCycles) {
			if(System.currentTimeMillis() - lastCycleTime >= 1000) {
				for(Police p : policeList){
					executorService.execute(p);
				}

				currentCycle++;
				lastCycleTime = System.currentTimeMillis();
			}
		}
		
		executorService.shutdown();
		try {
			executorService.awaitTermination(20000, TimeUnit.MILLISECONDS);
		} catch (InterruptedException e) {
			e.printStackTrace();
		}

		writePolice(policeOutFile, policeList);
		writeSuspects(suspectsOutFile, suspectsList);
		
		
	}
	
	//Output
	public static void writePolice(String filename, ArrayList<Police> policeList) {
		Formatter output = null;
		try {
			output = new Formatter(filename);
		} catch (SecurityException secExc) {
			System.err.println("Can't write to file");
			System.exit(1);
		} catch (FileNotFoundException fnfExc) {
			System.err.println("Can't find path to file");
			System.exit(1);
		}
		output.format("%s\n", "id,x.location,y.location,status,dog,suspect");
		for (Police p : policeList) {
			output.format("%s\n", p.returnStatus());
		}
		output.close();
		return;
	}
	
	public static void writeSuspects(String filename, ArrayList<Suspects> suspectList) {
		Formatter output = null;
		try {
			output = new Formatter(filename);
		} catch (SecurityException secExc) {
			System.err.println("Can't write to file");
			System.exit(1);
		} catch (FileNotFoundException fnfExc) {
			System.err.println("Can't find path to file");
			System.exit(1);
		}
		output.format("%s\n", "id,x.location,y.location,status,police unit");
		for (Suspects s : suspectList) {
			output.format("%s\n", s.returnStatus());
		}
		output.close();
		return;
	}
			
	public static void openFile(String filename) {
		try {
		    input = new Scanner(Paths.get(filename));
		} catch (IOException e) {
		    System.out.println("Can't find or read file");
		    return;
		}
	}
	
	public static ArrayList<Police> readPolice(ArrayList<Suspects> suspects) {
		ArrayList<Police> policeList = new ArrayList<Police>();
		while (input.hasNext()) {
			String currentLine = input.next();
			String[] inLine = currentLine.split(",");
			String badgeNumber = inLine[0];
			int xLoc = Integer.parseInt(inLine[1]);
			int yLoc = Integer.parseInt(inLine[2]);
			String status = inLine[3];
			//String dog = inLine[4];
			Boolean hasDog = (inLine[4].equalsIgnoreCase("yes")) ? true : false;
			Police p1 = new Police(badgeNumber, xLoc, yLoc, status, hasDog, suspects);
			policeList.add(p1);
		}
		return policeList;
	}
	
	public static ArrayList<Suspects> readSuspects() {
		ArrayList<Suspects> suspectsList = new ArrayList<Suspects>();
		while (input.hasNext()) {
			String currentLine = input.next();
			String[] inLine = currentLine.split(",");
			int id = Integer.parseInt(inLine[0]);
			int xLoc = Integer.parseInt(inLine[1]);
			int yLoc = Integer.parseInt(inLine[2]);
			String status = inLine[3];
			Suspects s1 = new Suspects(id, xLoc, yLoc, status);
			suspectsList.add(s1);
		}
		return suspectsList;
	}
	
}
