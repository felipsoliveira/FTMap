#!/usr/bin/env python3
import sys
sys.path.append('modules')

try:
    from workflow_manager import FTMapWorkflowManager
    print("✅ Import successful!")
    
    # Testar instanciação
    wf = FTMapWorkflowManager()
    print("✅ Instantiation successful!")
    
    # Testar status
    status = wf.get_workflow_status()
    print(f"✅ Status: {status}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
