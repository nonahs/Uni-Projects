package Part2;

import java.util.ArrayList;

import javax.swing.table.AbstractTableModel;

import java.awt.Point;


public class SimulationTableModel extends AbstractTableModel {
	
	private String[] columnNames = {"ID", "Location", "Status", "Has Dog", "Suspect ID"};
	private ArrayList<Police> policeList;
	
	public SimulationTableModel(ArrayList<Police> policeList ) {
		this.policeList = policeList;
	}
	
	public int getColumnCount() {
		return columnNames.length;
	}
	
	public String getColumnName(int col) {
		return columnNames[col];
	}
	
	public int getRowCount() {
		return policeList.size();
	}
	
	public Object getValueAt(int arg0, int arg1) {
		Police police = policeList.get(arg0);
		switch (arg1) {
		case 0:
			return police.getID();
		case 1:
			Point p = police.getLocation();
			int xCoord = (int) p.getX();
			int yCoord = (int) p.getY();
			return String.format("(%d,%d)", xCoord, yCoord);
		case 2:
			return police.getStatus();
		case 3:
			return (police.getDog()) ? "Yes" : "No"; //change dog from boolean back to yes/no
			//return police.getDog();
		case 4:
			if (police.getSuspectId() == 0) { //no unassigned suspects left
				return "-";
			} else {
			return police.getSuspectId();
			}
		}
		return null;
			
	}

}
