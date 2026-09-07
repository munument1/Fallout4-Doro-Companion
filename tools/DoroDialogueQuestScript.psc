Scriptname DoroDialogueQuestScript extends Quest

Event OnStageSet(int auiStageID, int auiItemID)
    ReferenceAlias speaker = GetAlias(0) as ReferenceAlias
    if speaker != None
        DoroCompanionScript doro = speaker.GetActorReference() as DoroCompanionScript
        if doro != None
            doro.DoCommand(auiStageID)
        endif
    endif
EndEvent
