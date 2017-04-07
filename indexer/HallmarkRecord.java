//####################
//   FileName:    HallmarkRecord.java
//   Author:      Simon Baker
//   Affiliation: University of Cambridge
//                Computer Laboratory and Language Technology Laboratory
//   Contact:     simon.baker.gen@gmail.com
//                simon.baker@cl.cam.ac.uk
//
//   Description: This class represents a hallmark annotation for a sentence

import java.util.ArrayList;
import java.util.Arrays;

import org.apache.poi.util.SystemOutLogger;

public class HallmarkRecord {
	public String sentID;
	public String hallmarkString;
	public String poistionString;

	public HallmarkRecord(String sentID, String positonString, String hallmarkString) {
		this.sentID = sentID.trim();
		hallmarkString = hallmarkString.replace(',', ' ');
		hallmarkString = hallmarkString.replace('a', 'x');
		this.poistionString = positonString.trim();
		this.hallmarkString = hallmarkString.trim();
	}

	public String getExpandedHallmarks() {
		String[] collapsedHM = this.hallmarkString.split(" ");
		ArrayList<String> expandedList = new ArrayList<String>();
		for (String colHM : collapsedHM) {
			if (expandedList.contains(colHM)) continue;
			
			for (int i = 1; i <= colHM.length(); i++) {
				String affix = colHM.substring(0, i);
				if (!expandedList.contains(affix)){
					expandedList.add(affix);
				}
			}
			
		}
		String retrunStr = "";
		for (String str : expandedList) {
			retrunStr += str + " "; 
		}
		return retrunStr.trim();
		
	}
	
	public static void main(String[] args) {
		String expanded = new HallmarkRecord("1", "", "9112,123").getExpandedHallmarks();
		System.out.println("expanded: " + expanded);
	}
//	
}
