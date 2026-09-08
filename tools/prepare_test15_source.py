"""Migrate the verified test14 source to the test15 combat hotfix."""
from pathlib import Path

root = Path(__file__).resolve().parent.parent
src = root / 'reference/test14_review/Source/Scripts/DoroCompanionScript.psc'
s = src.read_text(encoding='utf-8-sig')

def replace(old, new):
    global s
    assert s.count(old) == 1, old
    s = s.replace(old, new)

replace('Bool menuOpen = false', '''Bool menuOpen = false
Bool combatRequestPending = false
int combatRequests = 0
int friendlyStops = 0
int lastCombatState = 0
Actor lastCombatEventTarget
Bool clearedLegacyScene = false''')
replace('    SetCanDoCommand(false)\nEndFunction', '''    SetCanDoCommand(false)
    SetDoingFavor(false)
EndFunction''')
replace('    ; Keep reference scale neutral. test14 moves Doro size into DoroRace height.', '''    ; This mod now uses a message menu. Retire only its own obsolete dialogue scene.
    Scene legacyScene = Game.GetFormFromFile(0x0000080D, "DoroFollower.esp") as Scene
    if legacyScene != None && legacyScene.IsPlaying()
        legacyScene.Stop()
        clearedLegacyScene = true
    endif
    ; Keep test14 reference scale neutral. A/B differ only in RACE height.''')
replace('''        SetPlayerTeammate(true, true, true)
        if mode.GetValue() == 1.0''', '''        SetPlayerTeammate(true, false, true)
        if !IsInCombat() && mode.GetValue() == 1.0''')
replace('        elseif mode.GetValue() == 2.0', '        elseif !IsInCombat() && mode.GetValue() == 2.0')
replace('''    if akActionRef != Game.GetPlayer() || IsInCombat() || menuOpen
        return
    endif''', '''    if akActionRef != Game.GetPlayer() || menuOpen
        return
    endif
    if IsInCombat()
        ShowCombatStatus()
        return
    endif''')
replace('''    elseif choice == 4
        DoCommand(50)
    endif''', '''    elseif choice == 4
        DoCommand(50)
    elseif choice == 5
        ShowCombatStatus()
    endif''')
s = s.replace('SetPlayerTeammate(true, true, true)', 'SetPlayerTeammate(true, false, true)')
replace('    SetScale(1.0)', '''    if GetScale() != 1.0
        SetScale(1.0)
    endif''')
replace('    menuOpen = false\n    RegisterCombatEvents()', '''    menuOpen = false
    combatRequestPending = false
    RegisterCombatEvents()''')
replace('''    EnableAI(true)
    StartCombat(target, true)
EndFunction''', '''    ; Native combat owns retargeting once engaged. Repeated hits must not restart it.
    if IsInCombat() || combatRequestPending
        return
    endif
    combatRequestPending = true
    combatRequests += 1
    Debug.Trace("Doro test15: request combat against " + target)
    StartCombat(target, false)
    ; Cover the short interval before the engine reports the new combat state.
    StartTimer(1.0, 2)
EndFunction''')
replace('''    if aeCombatState > 0 && IsFriendlyTarget(akTarget)
        StopCombat()
    endif''', '''    lastCombatState = aeCombatState
    lastCombatEventTarget = akTarget
    Debug.Trace("Doro test15: combat state=" + aeCombatState + " target=" + akTarget)
    ; Searching or a missing/dead target is not proof that we attacked a friend.
    if aeCombatState == 1 && akTarget != None && !akTarget.IsDead()
        if IsFriendlyTarget(akTarget) && GetCombatTarget() == akTarget
            friendlyStops += 1
            Debug.Trace("Doro test15: stop combat against protected actor " + akTarget)
            StopCombat()
        endif
    endif''')
replace('''    if aiTimerID != 1
        return
    endif''', '''    if aiTimerID == 2
        combatRequestPending = false
        return
    endif
    if aiTimerID != 1
        return
    endif''')
s += '''
; Avoid engine object strings containing UI markup such as angle brackets.
string Function StatusFormId(Form value)
    if value == None
        return "None"
    endif
    return value.GetFormID() as string
EndFunction

; callable from the command menu, combat activation, or console cf ShowCombatStatus
Function ShowCombatStatus()
    if menuOpen
        return
    endif
    menuOpen = true
    Actor target = GetCombatTarget()
    float distance = -1.0
    if target != None
        distance = GetDistance(target)
    endif
    string info = "Doro test15 UI2 | state=" + GetCombatState() + " AI=" + IsAIEnabled()
    info += "\\nTargetID=" + StatusFormId(target) + " dist=" + (distance as int)
    info += "\\nPackageID=" + StatusFormId(GetCurrentPackage())
    info += "\\nSceneID=" + StatusFormId(GetCurrentScene()) + " cleared=" + clearedLegacyScene
    info += "\\nFavor=" + IsDoingFavor() + " drawn=" + IsWeaponDrawn()
    info += "\\nBleedout=" + IsBleedingOut() + " unconscious=" + IsUnconscious()
    info += "\\nStartCombat calls=" + combatRequests + " friendlyStops=" + friendlyStops
    info += "\\nLast event=" + lastCombatState + " targetID=" + StatusFormId(lastCombatEventTarget)
    Debug.Trace(info)
    Debug.MessageBox(info)
    menuOpen = false
EndFunction
'''
(root/'tools/DoroCompanionScript.psc').write_text(s, encoding='utf-8')
# Retain the current quest source as well; do not resurrect the 0.2.4 build pipeline.
q = src.with_name('DoroDialogueQuestScript.psc')
(root/'tools/DoroDialogueQuestScript.psc').write_bytes(q.read_bytes())
print('Prepared test15 source from verified test14')
